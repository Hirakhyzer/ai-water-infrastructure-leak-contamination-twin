% Plot synthetic water infrastructure digital twin metrics.
% Run the Python pipeline first so outputs/results exists.

scores = readtable('../outputs/results/synthetic_anomaly_scores.csv');
priority = readtable('../outputs/results/synthetic_response_priorities.csv');
robustness = readtable('../outputs/results/synthetic_robustness_tests.csv');

figure;
histogram(scores.overall_response_risk_score);
title('Synthetic water anomaly risk scores');
xlabel('Risk score');
ylabel('Sensor count');

figure;
bar(categorical(priority.priority_band));
title('Synthetic response priority bands');
ylabel('Count');

figure;
bar(categorical(robustness.stressor), robustness.mean_score_degradation);
title('Robustness degradation by stressor');
ylabel('Mean degradation');
