from abc import abstractmethod, ABC


class NCMClassifier(ABC):
    # def p_value(self, v, v_others):
    #     """
    #     Compute p-value of v with respect to v_others
    #     :param v: value
    #     :param v_others: reference values
    #     :return: p-value of v
    #     """
    #     return len(v_others[v_others >= v]) / len(v_others)

    # def calibrate(self, X_cal, y_cal, X_ref, y_ref):
    #     """
    #     Calibrating the set X_cal means computing the p-value for each of its point X_cal_i
    #     with respect to points of X_ref that have the same label: y_ref_i = y_cal_i and whose prediction is correct.
    #     :param X_cal: Calibration set
    #     :param y_cal: Calibration set labels
    #     :param X_ref: Reference set
    #     :param y_ref: Reference set labels
    #     :return: p-values of calibration set
    #     """
    #     # Compute NCM of reference samples
    #     y_ref_predict, ncm_ref = self.predict(X_ref), self.ncm(X_ref)
    #     # Predict labels for calibration points and compute their NCM
    #     y_cal_predict, ncm_cal = self.predict(X_cal), self.ncm(X_cal)
    #
    #     # For each calibration point get the class and compute the p-value
    #     # comparing its NCM with the ones of reference set whose ground-truth labels match the predicted class
    #     ncm_ref = ncm_ref[y_ref_predict == y_ref]
    #     y_ref = y_ref[y_ref_predict == y_ref]
    #     # Aggregate training NCM per class
    #     ncm_train_per_class = {label: ncm_ref[y_ref == label] for label in list(set(y_ref))}
    #
    #     # Compute the p-value for each calibration point
    #     return [self.p_value(ncm_cal[i], ncm_train_per_class[label]) for i, label in enumerate(y_cal_predict)]

    @abstractmethod
    def ncm(self, X, y):
        pass
