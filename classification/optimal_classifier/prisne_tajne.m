

truth = csvread('GT.dsv');
data = csvread('C4.dsv');

N = length(truth)/2;
P = length(truth)/2;

data_for_1 = data(truth == 1, :);
data_for_0 = data(truth == 0, :);

TP = sum(data_for_1);
FN = P - TP;
TN = sum(~data_for_0);
FP = N - TN;

TPR = TP ./ (TP + FN)
FPR = 1 - TN ./ (TN + FP)

figure
stem(FPR*100, TPR*100, 'LineStyle', 'None')
hold on
stem(0, 100, 'filled', 'LineStyle', 'None')
plot([-10 100], [100 100], 'black')
xlim([-5, 20])
ylim([-10 110])
title('ROC køivka pro klasifikátor C_4')
legend( 'ROC køivka', 'optimální klasifikace', 'location', 'southeast')
xlabel('False Positive Rate [%]')
ylabel('True Positive Rate [%]')
grid on


