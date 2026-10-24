LLM pricing trajectories include private_message for channel members.
Only detectors explicitly allowed private-channel access may read that field;
action-only detectors must ignore it. Ground truth is never detector input.
Pre-play messages are stored in ground_truth.private_chat at round -1;
trajectory private_message is the message chosen during that pricing round.
