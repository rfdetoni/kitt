#!/usr/bin/env python3
"""Verify installed Protocol / Proxy / Agent structured-result interoperability."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from kitt_protocol import AGENT_CONTRACT_VERSION
from kitt.llm.agent_contract import parse_structured_result
from kitt.goals.contract_validation import parse_validation_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proxy-runtime', type=Path, required=True)
    args = parser.parse_args()
    expected = [
        {'items': [{'title': 'Preserve "quotes", tabs\tand newlines\n'}]},
        {'verdict': 'OK', 'issues': []},
        {'verdict': 'OK', 'evidence': ['workspace inspected'], 'issues': []},
    ]
    # Host serialization at the real TypeScript boundary must be decoded by the
    # installed Python consumer, not by a second implementation in this script.
    javascript = r'''
import {pathToFileURL} from 'node:url';
import {readFileSync} from 'node:fs';
const root = process.argv[1];
const {AGENT_CONTRACT_VERSION} = await import(pathToFileURL(root + '/dist/contracts/agent-contract.js'));
const {prepareAgentContractRequest,transformAgentContractCompletion} = await import(pathToFileURL(root + '/dist/runtime/agent-contract.js'));
const values = JSON.parse(readFileSync(0, 'utf8'));
const plan = prepareAgentContractRequest({messages:[{role:'user',content:'Return a structured result'}]}, {sessionId:'composition-check'});
function encodeKAP(path, value, lines) {
  if (value === null) lines.push('NULL ' + path);
  else if (Array.isArray(value)) {
    lines.push('ARRAY ' + path);
    value.forEach((item,index)=>encodeKAP(path+'.'+index,item,lines));
  } else if (typeof value === 'object') {
    lines.push('OBJECT ' + path);
    for (const [key,item] of Object.entries(value)) encodeKAP(path+'.'+key,item,lines);
  } else if (typeof value === 'string' && value.includes('\n')) {
    lines.push('TEXT ' + path, value, 'KITT/ENDTEXT');
  } else if (typeof value === 'string') lines.push('STRING ' + path + ' = ' + value);
  else if (typeof value === 'boolean') lines.push('BOOLEAN ' + path + ' = ' + value);
  else lines.push((Number.isInteger(value)?'INTEGER ':'DECIMAL ') + path + ' = ' + value);
}
const content = values.map(value => {
  const lines = ['KITT/1','ACTION FINAL'];
  encodeKAP('content',value,lines);
  const kap = [...lines,'KITT/END'].join('\n');
  return transformAgentContractCompletion({
    id:'check',object:'chat.completion',created:1,model:'check',
    choices:[{index:0,message:{role:'assistant',content:kap},finish_reason:'stop'}]
  },plan).choices[0].message.content;
});
console.log(JSON.stringify({version:AGENT_CONTRACT_VERSION,content}));
'''
    result = subprocess.run(
        ['node', '--input-type=module', '-e', javascript, str(args.proxy_runtime.resolve())],
        input=json.dumps(expected), capture_output=True, text=True, check=True, timeout=30,
    )
    payload = json.loads(result.stdout.splitlines()[-1])
    if payload['version'] != AGENT_CONTRACT_VERSION:
        raise SystemExit('installed Agent / Protocol / Proxy contract version mismatch')
    actual = [parse_structured_result(content) for content in payload['content']]
    if actual != expected or not parse_validation_report(payload['content'][2]).ok:
        raise SystemExit('structured results changed across the installed runtime boundary')
    print('installed Agent / Protocol / Proxy structured results: ok')


if __name__ == '__main__':
    main()
