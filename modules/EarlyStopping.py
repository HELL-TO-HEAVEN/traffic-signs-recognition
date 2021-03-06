import numpy as np
import os
from .utils import utils


class EarlyStopping(object):
    def __init__(self, model, optimizer, params=None, patience=100, minimize=True):
        self.minimize = minimize
        self.patience = patience
        self.model = model
        self.optimizer = optimizer
        self.params = params
        self.best_monitored_value = np.inf if minimize else 0.
        self.best_monitored_acc = 0. if minimize else np.inf
        self.best_monitored_epoch = 0

        self.restore_path = None

    def __call__(self, value, acc, epoch, rest):
        if (self.minimize and value < self.best_monitored_value) or (not self.minimize and value > self.best_monitored_value):
            self.best_monitored_value = value
            self.best_monitored_epoch = epoch
            self.best_monitored_acc = acc

            state = {
                'params': self.params,
                'epoch': epoch + 1,
                'state_dict': self.model.state_dict(),
                'best': value,
                'best_acc': acc,
                'optimizer': self.optimizer.state_dict(),
            }

            rest.update(state)
            print(value, acc)
            self.restore_path = utils.save_checkpoint(
                rest, True, os.path.join(self.params.save_loc, "early_stopping_checkpoint"))
        elif self.best_monitored_epoch + self.patience < epoch:
            if self.restore_path is not None:
                checkpoint = utils.load_checkpoint(self.restore_path)
                self.best_monitored_value = checkpoint['best']
                self.best_monitored_acc = checkpoint['best_acc']
                self.best_monitored_epoch = checkpoint['epoch']
                self.model.load_state_dict(checkpoint['state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer'])
            else:
                print("ERROR: Failed to restore session")
            return True

        return False

    def init_from_checkpoint(self, checkpoint):
        self.best_monitored_value = checkpoint['best']
        self.best_monitored_acc = checkpoint['best_acc']
        self.best_monitored_epoch = 0

        if "params" in checkpoint:
            self.params = checkpoint['params']

    def print_info(self):
        print("Best loss: {0}, Best Accuracy: {1}, at epoch {2}"
              .format(self.best_monitored_value,
                      self.best_monitored_acc,
                      self.best_monitored_epoch))
