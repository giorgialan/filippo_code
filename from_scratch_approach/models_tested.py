import torch

"This file includes the definitions of the six models tested."

##Convolutional models
#Model with convolutional and LSTM layers

class lstm_conv_AE(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size, kernel_size, stride, padding):
        super(lstm_conv_AE, self).__init__()


        # Encoder
        self.encoder = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=input_size, out_channels=hidden_size[0, 0], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.Conv1d(in_channels=hidden_size[0, 0], out_channels=hidden_size[0, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.Conv1d(in_channels=hidden_size[0, 1], out_channels=hidden_size[0, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.Conv1d(in_channels=hidden_size[0, 2], out_channels=output_size, kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
        )

        # LSTM layer
        self.lstm = torch.nn.LSTM(input_size=64, hidden_size=64, num_layers=1, batch_first=True)

        # Decoder
        self.decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose1d(in_channels=output_size, out_channels=hidden_size[1, 0], kernel_size=kernel_size, stride=2, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 0], out_channels=hidden_size[1, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 1], out_channels=hidden_size[1, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 2], out_channels=input_size, kernel_size=kernel_size, stride=stride, padding=padding)
        )

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x = self.encoder(x)
        x = fill_with_zeros(x)
        x = np.swapaxes(x,i,j)
        x, ras = self.lstm(x)
        x = torch.nn.functional.relu(x)
        x = np.swapaxes(x,i,j)
        x = self.decoder(x)
        x = np.swapaxes(x,i,j)
        return x

#Model with convolutional layers and without LSTM layer

class conv_AE(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size, kernel_size, stride, padding):
        super(conv_AE, self).__init__()

        # Encoder
        self.encoder = torch.nn.Sequential(
            torch.nn.Conv1d(in_channels=input_size, out_channels=hidden_size[0, 0], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.Conv1d(in_channels=hidden_size[0, 0], out_channels=hidden_size[0, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.Conv1d(in_channels=hidden_size[0, 1], out_channels=hidden_size[0, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.Conv1d(in_channels=hidden_size[0, 2], out_channels=output_size, kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
        )

        # Decoder
        self.decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose1d(in_channels=output_size, out_channels=hidden_size[1, 0], kernel_size=kernel_size, stride=3, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 0], out_channels=hidden_size[1, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 1], out_channels=hidden_size[1, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 2], out_channels=input_size, kernel_size=kernel_size, stride=stride, padding=padding)
        )

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x = self.encoder(x)
        x = self.decoder(x)
        x = np.swapaxes(x,i,j)
        return x


##Resnet models

#Function to adapt x, allowing to add it to a convolutional layer with stride=2

def divide(x, stride) :
    if len(x.size())==3 :
      n,m,p=x.size()
      res=torch.Tensor(np.zeros((n,m*2,p//stride+1)))
      for i in range(n) :
        for j in range(m) :
          res[i,2*j,:]=x[i,j,::stride]
          res[i,2*j+1,:]=x[i,j,::stride]
    else :
      n,m=x.size()
      res=torch.Tensor(np.zeros((n*2,m//stride+1)))
      for i in range(n) :
        res[2*i,:]=x[i,::stride]
        res[2*i+1,:]=x[i,::stride]
    return res.to(device)

#Definition of a ResnetBlock

class ResBlockEncoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, padding):
        super().__init__()

        self.conv1 = torch.nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=padding, groups=in_channels)

    def forward(self, input):
        id = divide(input, stride)
        input = self.conv1(input)
        return input + id

#Model with Resnet and LSTM layers

class lstm_resnet_AE(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size, kernel_size, stride, padding):
        super(lstm_resnet_AE, self).__init__()

        # Encoder
        self.encoder = torch.nn.Sequential(
            ResBlockEncoder(in_channels=input_size, out_channels=hidden_size[0, 0], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            ResBlockEncoder(in_channels=hidden_size[0, 0], out_channels=hidden_size[0, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            ResBlockEncoder(in_channels=hidden_size[0, 1], out_channels=hidden_size[0, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            ResBlockEncoder(in_channels=hidden_size[0, 2], out_channels=output_size, kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
        )

        # LSTM layer
        self.lstm = torch.nn.LSTM(input_size=64, hidden_size=64, num_layers=3, batch_first=True)

        # Decoder
        self.decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose1d(in_channels=output_size, out_channels=hidden_size[1, 0], kernel_size=kernel_size, stride=2, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 0], out_channels=hidden_size[1, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 1], out_channels=hidden_size[1, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 2], out_channels=input_size, kernel_size=kernel_size, stride=stride, padding=padding)
        )
    def forward(self, x):
      if len(x.size())==3 :
        i,j=1,2
      else :
        i,j=0,1
      x = np.swapaxes(x,i,j)
      x = self.encoder(x)
      x = fill_with_zeros(x)
      x = np.swapaxes(x,i,j)
      x, ras = self.lstm(x)
      x = np.swapaxes(x,i,j)
      x = self.decoder(x)
      x = np.swapaxes(x,i,j)
      return x

#Model with Resnet layers and without LSTM layers

class resnet_AE(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size, kernel_size, stride, padding):
        super(resnet_AE, self).__init__()
        # self.lstm_instance = LSTM(input_size_lstm, output_size_lstm, hidden_dim_lstm, n_layers_lstm)

        # Encoder
        self.encoder = torch.nn.Sequential(
            ResBlockEncoder(in_channels=input_size, out_channels=hidden_size[0, 0], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            ResBlockEncoder(in_channels=hidden_size[0, 0], out_channels=hidden_size[0, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            ResBlockEncoder(in_channels=hidden_size[0, 1], out_channels=hidden_size[0, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            ResBlockEncoder(in_channels=hidden_size[0, 2], out_channels=output_size, kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
        )

        # Decoder
        self.decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose1d(in_channels=output_size, out_channels=hidden_size[1, 0], kernel_size=kernel_size, stride=3, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 0], out_channels=hidden_size[1, 1], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 1], out_channels=hidden_size[1, 2], kernel_size=kernel_size, stride=stride, padding=padding),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(in_channels=hidden_size[1, 2], out_channels=input_size, kernel_size=kernel_size, stride=stride, padding=padding)
        )

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x = self.encoder(x)
        x = self.decoder(x)
        x = np.swapaxes(x,i,j)
        return x

## Linear models

#Encoder with Linear layers
class linear_encoder(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.linear1 = torch.nn.Linear(161, 128)
        self.linear2 = torch.nn.Linear(128, 64)
        self.linear3 = torch.nn.Linear(64, 36)
        self.linear4 = torch.nn.Linear(36, 18)
        self.linear5 = torch.nn.Linear(18, 9)

    def reset_parameters(self):
        list_layer=[self.linear1,self.linear2,self.linear3,self.linear4,self.linear5]
        for layer in list_layer:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x = self.linear1(x)
        x = torch.nn.functional.relu(x)
        x = self.linear2(x)
        x = torch.nn.functional.relu(x)
        x = self.linear3(x)
        x = torch.nn.functional.relu(x)
        x = self.linear4(x)
        x = torch.nn.functional.relu(x)
        x = self.linear5(x)
        x = torch.nn.functional.relu(x)
        x = np.swapaxes(x,i,j)
        return x

#Decoder with Linear layers

class linear_decoder(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.linear1 = torch.nn.Linear(9, 18)
        self.linear2 = torch.nn.Linear(18, 36)
        self.linear3 = torch.nn.Linear(36, 64)
        self.linear4 = torch.nn.Linear(64, 128)
        self.linear5 = torch.nn.Linear(128, 241)

    def reset_parameters(self):
        list_layer=[self.linear1,self.linear2,self.linear3,self.linear4,self.linear5]
        for layer in list_layer:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x = self.linear1(x)
        x = torch.nn.functional.relu(x)
        x = self.linear2(x)
        x = torch.nn.functional.relu(x)
        x = self.linear3(x)
        x = torch.nn.functional.relu(x)
        x = self.linear4(x)
        x = torch.nn.functional.relu(x)
        x = self.linear5(x)
        x = np.swapaxes(x,i,j)
        return x

#Definition of LSTM layer
def c_lstm(input_size, hidden_size) :
  return torch.nn.LSTM(input_size=input_size, hidden_size=hidden_size,num_layers=1,batch_first=True,dropout=0.0)

#Encoder with LSTM layers

class lstm_encoder(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.lstm1 = c_lstm(161, 128)
        self.lstm2 = c_lstm(128, 100)
        self.lstm3 = c_lstm(100, 80)
        self.lstm4 = c_lstm(80, 60)
        self.lstm5 = c_lstm(60, 50)

    def reset_parameters(self):
        list_layer=[self.lstm1,self.lstm2,self.lstm3,self.lstm4,self.lstm5]
        for layer in list_layer:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x,ras = self.lstm1(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm2(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm3(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm4(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm5(x)
        x = torch.nn.functional.relu(x)
        x = np.swapaxes(x,i,j)
        return x

#Decoder with LSTM layers

class lstm_decoder(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.lstm1 = c_lstm(50, 60)
        self.lstm2 = c_lstm(60, 80)
        self.lstm3 = c_lstm(80, 100)
        self.lstm4 = c_lstm(100, 128)
        self.lstm5 = c_lstm(128, 241)

    def reset_parameters(self):
        list_layer=[self.lstm1,self.lstm2,self.lstm3,self.lstm4,self.lstm5]
        for layer in list_layer:
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()

    def forward(self, x):
        if len(x.size())==3 :
          i,j=1,2
        else :
          i,j=0,1
        x = np.swapaxes(x,i,j)
        x,ras = self.lstm1(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm2(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm3(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm4(x)
        x = torch.nn.functional.relu(x)
        x,ras = self.lstm5(x)
        x = np.swapaxes(x,i,j)
        return x