from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras import optimizers, metrics
from tensorflow.keras.regularizers import L1L2
from tensorflow.keras.callbacks import EarlyStopping


def init_model(pred_type, input_length, opti='adam', lr=0.02,
               rm_rho=0.9, rm_mo=0, q_features=27):

    # $CHALLENGIFY_BEGIN

    # 0 - Normalization
    # ======================
    #normalizer = Normalization()
    #normalizer.adapt(X_train)

    # 1 - RNN architecture
    # ======================
    model = models.Sequential()
    ## 1.0 - All the rows will be standardized through the already adapted normalization layer
    #model.add(normalizer)
    ## 1.1 - Recurrent Layer
    model.add(layers.GRU(128,
                          activation='tanh',
                          return_sequences = False,
                          #kernel_regularizer=L1L2(l1=0.05, l2=0.05),
                          input_shape=(input_length, q_features)
                          ))
    model.add(layers.Dropout(0.4))

    ## 1.2 - Predictive Dense Layers
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(128, activation='relu'))
    #model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dropout(0.8))
    #output_length = y_train.shape[1]
    output_length = 1
    if pred_type == 'reg':
      model.add(layers.Dense(output_length, activation='linear'))
    else:
      model.add(layers.Dense(output_length, activation='sigmoid'))

    # 2 - Compiler
    # ======================
    adam = optimizers.Adam(learning_rate=lr)
    rmsprop = optimizers.experimental.RMSprop(learning_rate=lr,
                                              rho=rm_rho,
                                              momentum=rm_mo)
    if pred_type == 'reg':
      model.compile(loss='mae', optimizer=opti, metrics=['mse'])
    else:
      model.compile(loss='binary_crossentropy', optimizer=opti,
                    metrics=['accuracy'])

    return model


def fit_model(model, X_train, y_train,
              epochs, patience, validation_split=0.3,
              verbose=1):
    es = EarlyStopping(monitor = "val_loss",
                      patience = patience,
                      restore_best_weights = True)

    history = model.fit(X_train, y_train,
                        validation_split = validation_split,
                        shuffle = False,
                        batch_size = 32,
                        epochs = epochs,
                        callbacks = [es],
                        verbose = verbose)

    return model, history


def cross_validate(data, ticker, list_years, pred_type, epochs,
                   seq_stride, target, input_length,
                   fold_length=None, fold_stride=None, patience=50,
                   train_test_ratio=0.7, output_length=1,
                   q_features=27
                   ):
    '''
    This function cross-validates a model
    '''
    data_train, data_test = data_transform(data, ticker, list_years, target)
    #list_of_mae_recurrent_model = []

    model = init_model(pred_type=pred_type, input_length=input_length,
                       opti='rmsprop', q_features=q_features)
    # In case folds exist:
    if fold_length != None:
      folds = get_folds(data_train, fold_length, fold_stride)
      for fold_id, fold in enumerate(folds):
          print(f'Processing fold {fold_id}')
          # 1 - Train/Test split the current fold
          # =========================================
          (fold_train, fold_test) = train_test_split(fold, train_test_ratio,
                                                     input_length)
          X_train, y_train = get_X_y_strides(fold_train, input_length,
                                             output_length, seq_stride)
          # 2 - Modelling per fold
          # =========================================
          model, history = fit_model(model, X_train, y_train, epochs=epochs,
                                    patience=patience)

    # In case of NOT using folds
    if fold_length == None:
      # 1 - Train/Test split the current fold
      # =========================================
      X_train, y_train = get_X_y_strides(data_train, input_length,
                                        output_length, seq_stride)
      # 2 - Modelling without folds
      # =========================================
      model, history = fit_model(model, X_train, y_train, epochs=epochs,
                                patience=patience)
    #X_test, y_test = get_X_y_strides(data_test, input_length,
    #                                 output_length, seq_stride)
    #res = model.evaluate(X_test, y_test, verbose=0)
    #mae_lstm = res[1]
    #list_of_mae_recurrent_model.append(mae_lstm)

    return model, history#, res
