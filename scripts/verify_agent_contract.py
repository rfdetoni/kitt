#!/usr/bin/env python3
"""Verify installed Protocol / Proxy / Agent JSON interoperability."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from kitt_protocol import AGENT_CONTRACT_VERSION
from kitt.llm.agent_contract import parse_structured_result
from kitt.goals.contract_validation import parse_validation_report
from kitt.tools.protocol import parse_tool_call


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proxy-runtime', type=Path, required=True)
    args = parser.parse_args()
    expected = [
        {'items': [{'title': 'Preserve "quotes", tabs\tand newlines\n'}]},
        {'verdict': 'OK', 'issues': []},
        {'verdict': 'OK', 'evidence': ['workspace inspected'], 'issues': []},
        {'verdict': 'FAIL', 'evidence': ['current file inspected'], 'issues': [{
            'severity': 'P1', 'location': 'src/domain.ts',
            'problem': 'requirement is unproven', 'fix': 'implement and validate it',
        }]},
        {'tasks': [{'local_id': 'T01', 'check_ids': ['node.typecheck']}],
         'X-Foo': 'enabled', 'data': 'literal {braces}, Unicode ação 😀 and backslash \\n'},
    ]
    # Real TypeScript transform followed by real installed Python consumers.
    javascript = r'''
import {pathToFileURL} from 'node:url';
import {readFileSync} from 'node:fs';
const root = process.argv[1];
const {AGENT_CONTRACT_VERSION} = await import(pathToFileURL(root + '/dist/contracts/agent-contract.js'));
const {prepareAgentContractRequest,transformAgentContractCompletion} = await import(pathToFileURL(root + '/dist/runtime/agent-contract.js'));
const values = JSON.parse(readFileSync(0, 'utf8'));
const toolInput = {operation:'repo.read',arguments:{path:'README.md'}};
const plan = prepareAgentContractRequest({messages:[{role:'user',content:'Return a structured result'}],tools:[{type:'function',function:{name:'kitt_runtime',parameters:{type:'object',properties:{operation:{enum:['repo.read']},arguments:{type:'object',properties:{path:{type:'string'}},required:['path'],additionalProperties:false}},required:['operation','arguments'],additionalProperties:false}}}]}, {sessionId:'composition-check'});
const envelope = (action,content,tool=null,tool_input=null) => ({action,tool,tool_input,content,reasoning_summary:'',loop:null});
const completion = content => ({id:'check',object:'chat.completion',created:1,model:'check',choices:[{index:0,message:{role:'assistant',content},finish_reason:'stop'}]});
const transform = value => transformAgentContractCompletion(completion(JSON.stringify(value)),plan).choices[0].message;
const content = values.map(value => transform(envelope('final_response',value)).content);
const action = envelope('use_tool',null,'kitt_runtime',toolInput);
const tool = transform(action).tool_calls[0].function;
for (const raw of [JSON.stringify(action).replace('"path":"README.md"','"path":"README.md","path":"secret"'),JSON.stringify(action)+'\n'+JSON.stringify(envelope('final_response','done'))]) {
  let rejected = false;
  try { transformAgentContractCompletion(completion(raw),plan); } catch { rejected = true; }
  if (!rejected) throw new Error('Conflicting JSON model output was accepted');
}
console.log(JSON.stringify({version:AGENT_CONTRACT_VERSION,content,action,tool}));
'''
    result = subprocess.run(
        ['node', '--input-type=module', '-e', javascript, str(args.proxy_runtime.resolve())],
        input=json.dumps(expected), capture_output=True, text=True, check=True, timeout=30,
    )
    payload = json.loads(result.stdout.splitlines()[-1])
    if payload['version'] != AGENT_CONTRACT_VERSION:
        raise SystemExit('installed Agent / Protocol / Proxy contract version mismatch')
    actual = [parse_structured_result(content) for content in payload['content']]
    failed_review = parse_validation_report(payload['content'][3])
    tool = payload['tool']
    if (actual != expected or not parse_validation_report(payload['content'][2]).ok
            or failed_review.ok or failed_review.issues[0]['location'] != 'src/domain.ts'
            or tool['name'] != 'kitt_runtime'
            or json.loads(tool['arguments']) != payload['action']['tool_input']
            or parse_tool_call(json.dumps(payload['action'])) != ('kitt_runtime',payload['action']['tool_input'])):
        raise SystemExit('JSON changed across the installed runtime boundary')
    print('installed Agent / Protocol / Proxy JSON results and tool actions: ok')


if __name__ == '__main__':
    main()
