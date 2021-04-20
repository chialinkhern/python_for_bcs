import numpy as np
import matplotlib.pyplot as plt
import random


############################################################################################################
############################################################################################################
class LogisticRegression:
    ############################################################################################################
    def __init__(self, dataset, learning_rate, num_epochs, verbose, output_filename):

        self.name = "logistic_regression"

        self.dataset = dataset
        self.output_filename = output_filename

        self.train_xy_list = None
        self.test_xy_list = None

        self.input_size = None
        self.output_size = None
        self.weight_mean = 0
        self.weight_stdev = 0.1
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.verbose = verbose
        self.output_freq = 1

        self.y_bias = None
        self.y_x_weights = None

        self.training_accuracy = None
        self.training_confidence = None
        self.training_sse = None
        self.test_accuracy = None
        self.test_confidence = None
        self.test_sse = None

        self.init_network()
        self.prep_data()

    ############################################################################################################
    def init_network(self):

        if self.dataset.svd_dimensions:
            self.input_size = self.dataset.svd_dimensions
        else:
            self.input_size = self.dataset.num_features
        self.output_size = self.dataset.num_categories
        self.y_bias = np.random.normal(self.weight_mean, self.weight_stdev, [self.output_size])
        self.y_x_weights = np.random.normal(self.weight_mean, self.weight_stdev, [self.output_size, self.input_size])
        print()
        print("Creating Logistic Regression Model with {} inputs and {} outputs for {} epochs".format(self.input_size,
                                                                                                      self.output_size,
                                                                                                      self.num_epochs))

    ############################################################################################################
    def prep_data(self):
        self.train_xy_list = []
        for i in range(self.dataset.training_size):
            feature_vector = self.dataset.feature_matrix[self.dataset.training_list[i][0]]
            category_vector = self.dataset.category_matrix[self.dataset.training_list[i][0]]
            self.train_xy_list.append((feature_vector, category_vector))

        self.test_xy_list = []
        for i in range(self.dataset.test_size):
            feature_vector = self.dataset.feature_matrix[self.dataset.test_list[i][0]]
            category_vector = self.dataset.category_matrix[self.dataset.test_list[i][0]]
            self.test_xy_list.append((feature_vector, category_vector))

    ############################################################################################################
    def train(self):
        print("    Training Model")
        sse = 0
        accuracy_sum = 0
        confidence_sum = 0

        for i in range(self.num_epochs):
            sse = 0
            accuracy_sum = 0
            confidence_sum = 0

            for j in range(self.dataset.training_size):
                correct_category = self.dataset.training_list[j][1]
                x = self.train_xy_list[j][0]
                y_actual = self.train_xy_list[j][1]

                y_pred = self.feedforward(x)

                category_prediction, accuracy, confidence = self.evaluate(y_pred, correct_category)
                accuracy_sum += accuracy
                confidence_sum += confidence

                error = self.calc_error(y_actual, y_pred)
                sse += (error**2).sum()

                if i % self.output_freq == 0 and j == self.dataset.training_size-1:
                    if self.verbose:
                        accuracy_mean = accuracy_sum / self.dataset.training_size
                        confidence_mean = confidence_sum / self.dataset.training_size
                        self.output_epoch(i, accuracy_mean, confidence_mean, sse)
                    else:
                        print("        Epoch: {}   SSE: {:0.3f}".format(i, sse))

                self.delta_rule(x, y_pred, error)

        if self.verbose:
            accuracy_mean = accuracy_sum / self.dataset.training_size
            confidence_mean = confidence_sum / self.dataset.training_size
            self.output_epoch(self.num_epochs, accuracy_mean, confidence_mean, sse)
        else:
            print("        Epoch: {}   SSE: {:0.3f}".format(self.num_epochs, sse))

        self.training_accuracy = accuracy_sum / self.dataset.training_size
        self.training_confidence = confidence_sum / self.dataset.training_size
        self.training_sse = sse / self.dataset.training_size

        print()
        print("        Final Training Performance:")
        print("            Accuracy:       {:0.3f}".format(self.training_accuracy))
        print("            Confidence:     {:0.3f}".format(self.training_confidence))
        print("            Mean SS Error:  {:0.3f}".format(sse/self.dataset.training_size))

        if self.verbose:
            print("\n        Individual Word Results")
            print("            Word           CorrectCat     GuessCat    Accuracy    Confidence   Error")
            for i in range(self.dataset.training_size):
                word = self.dataset.training_list[i][2]
                correct_category = self.dataset.training_list[i][1]
                x = self.train_xy_list[i][0]
                y_actual = self.train_xy_list[i][1]
                y_pred = self.feedforward(x)
                category_prediction, accuracy, confidence = self.evaluate(y_pred, correct_category)
                error = self.calc_error(y_actual, y_pred)
                print("            {:14s} {:14s} {:14s} {:4s}     {:0.3f}        {:0.3f}".format(word,
                                                                                             correct_category,
                                                                                             category_prediction,
                                                                                             str(accuracy),
                                                                                             confidence,
                                                                                             (error**2).sum()))

    ############################################################################################################
    def test(self):
        print()
        print("        Test Performance:")

        acc_sum = 0
        conf_sum = 0
        sse = 0

        verbose_output_list = []

        for i in range(self.dataset.test_size):
            word = self.dataset.test_list[i][2]
            correct_category = self.dataset.test_list[i][1]
            x = self.test_xy_list[i][0]
            y_actual = self.test_xy_list[i][1]
            y_pred = self.feedforward(x)
            category_prediction, accuracy, confidence = self.evaluate(y_pred, correct_category)
            acc_sum += accuracy
            conf_sum += confidence
            error = self.calc_error(y_actual, y_pred)
            sse += (error**2).sum()
            output_string = "            {:14s} {:14s} {:14s} {:4s}     {:0.3f}        {:0.3f}".format(word,
                                                                                                   correct_category,
                                                                                                   category_prediction,
                                                                                                   str(accuracy),
                                                                                                   confidence,
                                                                                                   (error**2).sum())
            verbose_output_list.append(output_string)

        self.test_accuracy = acc_sum / self.dataset.test_size
        self.test_confidence = conf_sum / self.dataset.test_size
        self.test_sse = sse/self.dataset.test_size


        print("            Summary")
        print("                Accuracy:   {:0.3f}".format(self.test_accuracy))
        print("                Confidence: {:0.3f}".format(self.test_confidence))
        print("                Mean SSE:   {:0.3f}".format(self.test_sse))

        if self.verbose:
            print("\n        Individual Word Results")
            print("            Word           CorrectCat     GuessCat    Accuracy    Confidence   Error")
            for output_string in verbose_output_list:
                print(output_string)

    ############################################################################################################
    @staticmethod
    def output_epoch(i, accuracy_mean, confidence_mean, sse):
        if i % 10 == 0:
            print("        Epoch {}:   Accuracy: {:0.3f}   Confidence: {:0.3f}   SSE: {:0.3f}".format(i,
                                                                                                  accuracy_mean,
                                                                                                  confidence_mean,
                                                                                                  sse))

    ############################################################################################################
    def feedforward(self, x):
        y = self.sigmoid(np.dot(self.y_x_weights, x) + self.y_bias)
        return y

    ############################################################################################################
    def evaluate(self, y_pred, correct_category):
        category_prediction = self.dataset.category_list[np.argmax(y_pred)]
        if correct_category == category_prediction:
            accuracy = 1
        else:
            accuracy = 0
        confidence = np.max(y_pred) / y_pred.sum()

        return category_prediction, accuracy, confidence

    ############################################################################################################
    @staticmethod
    def calc_error(y_actual, y_pred):
        return y_actual - y_pred

    ############################################################################################################
    def delta_rule(self, x, y, y_error):
        y_delta = y_error * self.sigmoid_prime(y)

        # change all these to -=
        self.y_bias += y_delta * self.learning_rate
        self.y_x_weights += (np.dot(y_delta.reshape(len(y_delta), 1), x.reshape(1, len(x))) * self.learning_rate)

    ############################################################################################################
    @staticmethod
    def sigmoid(z):
        return 1/(1+np.exp(-z))

    ############################################################################################################
    @staticmethod
    def sigmoid_prime(z):
        return 1/(1+np.exp(-z)) * (1 - 1/(1+np.exp(-z)))

    ###########################################################################
    def write_results(self):
        f = open(self.output_filename, 'a')
        f.write("{},{},{},{},{},{},{},{},{}_{},{},{}\n".format(self.name, self.random_seed,
                                                                  self.dataset.num_features,
                                                                  self.dataset.num_categories,
                                                                  self.dataset.num_words,
                                                                  self.dataset.training_size,
                                                                  self.dataset.normalize_data,
                                                                  self.dataset.svd_dimensions,
                                                                  self.learning_rate, self.num_epochs,
                                                                  self.training_accuracy,
                                                                  self.test_accuracy))
        f.close()