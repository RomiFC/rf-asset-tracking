clear
clc

% Inputting data from datalog(0,1).csv
datalog = readmatrix('datalog(0,1).csv', "Delimiter", ' ', "VariableNamingRule", "Preserve");

% Data processing
RSSI = datalog(:, 3);
phase = datalog(:, 7);

mu_RSSI = mean(RSSI);
sigma_RSSI = std(RSSI);
norm_RSSI = fitdist(RSSI, 'Normal');         % Normal distribution fitting
x_RSSI = linspace(-65, -48, length(RSSI));   % X values using RSSI vector size
p_RSSI = pdf(norm_RSSI, x_RSSI);             % Gaussian PDF of RSSI from mu and sigma

figure(1)
tiledlayout('flow');
nexttile
histogram(RSSI, 'BinMethod', 'integers', 'Normalization', 'probability')
    grid on
    xlabel('RSSI (dBm)');
    ylabel('Probability mass/density of RSSI');
    hold on
plot(x_RSSI, p_RSSI, 'LineWidth', 2)
    grid on
    hold off

    
nexttile
histogram(phase, 'BinLimits', [156, 180], 'Normalization', 'probability')
    grid on
    xlabel('Phase (Degrees)');
    ylabel('Probability mass of phase');
    









