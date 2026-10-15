# KITT 0.16.5 — bounded planning and local JSON result normalization

Pins Agent CLI 0.88.1, Reverse Proxy 5.4.4, Assistant 0.1.46 / Runtime 0.4.1 and Workers / Evals / Evolution 0.1.78. Updated runtime and consumer locks resolve the same Agent commit. Protocol 0.14.0 remains JSON Agent v5; Memory and Toolbox pins are unchanged.

Automatic planning uses one model generation and existing local structural checks. One correction is allowed for an invalid structure; mandatory LLM plan review/revision loops are removed. The planner receives no execution tools and skips the advisory Architect call. Execution retains host approvals, deterministic checks, independent code/task validation and final integration verification.

The Proxy mechanically wraps a complete strict plain JSON result in `final_response.content` without another model call and excludes provider-native tool recipients and non-final channels from assistant result capture. Late channel/recipient classification invalidates earlier text from that message.
