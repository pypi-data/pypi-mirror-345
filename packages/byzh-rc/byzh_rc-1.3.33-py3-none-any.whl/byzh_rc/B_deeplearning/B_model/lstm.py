import torch
import torch.nn as nn

class BLSTM(nn.Module):
    def __init__(self, num_classes, input_size, hidden_size, num_layers=1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
        )
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        # x [batch_size, input_size, seq_len]
        x = x.permute(2, 0, 1)
        # x [seq_len, batch_size, input_size]
        out, (h, c) = self.lstm(x)  # out: [seq_len, batch_size, hidden_size]
        # 取最后一个时间步的输出作为整个序列的表示
        out = out[-1]
        out = self.fc(out)
        return out

if __name__ == '__main__':
    model = BLSTM(num_classes=11, input_size=2, hidden_size=512, num_layers=4)
    x = torch.randn(32, 2, 128)  # 输入形状 [batch_size, input_size, seq_len]
    y = model(x)
    print(y.shape)
