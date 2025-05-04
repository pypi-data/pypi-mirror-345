import logging
import os
from queue import Queue
import threading
from .extract import Extract


class Function(Extract):
    """
    Base class to define function in module

    Based on Extract, it supoprt all the extract method.
    It is necessary to set the files or directory to process
    before calling the process method.

    Evaluate method should be overwritten for data evaluation
    related to the function beeing developed.
    """

    def __init__(self, dataset=dict()):
        self.dataset = dataset
        super().__init__()
        self.module = self.__class__.__module__
        self.evals = Queue()
        self.extract_thread = threading.Thread(target=self._run_extract)
        self.extract_thread.daemon = True
        self.extract_thread.start()

        #super().start()
        # self.__class__.__name__
        # self.log=Log(self.module)

    def _run_extract(self):
        """
        Run Extract's run method to process files and populate self.data.
        """
        super().run()  # Call Extract.run

    def process(self):
        """
        Retrieve the necessary information from the measurment files.

        :return: list containing files processed results
        """
        res = dict()
        for filename in self.files:
            print(filename)
            self.set_file(filename)
            path, filename = os.path.split(filename)
            filename = filename.split(".")[0]
            data = self.get_data()

            if len(data.index) == 0:
                logging.debug("No data found")
                continue
            eval = self.evaluate(data)
            if len(eval.index) != 0:
                res[filename] = eval
        return res

    def evaluate(self, data):
        """
        Using the data retrieved from the measurement file, generate calibration
        This method should be over writen by the derivative class and
        returns what ever the evaluation is producing.

        :return: should return the evaluation data
        """
        return data

    def lab(self):
        """
        Write the labels and parameters in a lab file

        :return: None
        """
        f = open("%s.lab" % self.module, "w", encoding="utf-8")
        f.write("[RAMCELL]\n")
        for index, row in self.channels.iterrows():
            f.write("%s\n" % row["channel"])
        f.write("\n")

        if self.dataset.keys():
            f.write("[LABEL]\n")
            for key in self.dataset.keys():
                f.write("%s\n" % key)
        f.close()

    def start(self):
        super().start()
        return self.files, self.evals

    def run(self):
        while True:
            #try:
            filename, data = self.data.get()
            result = self.evaluate(data)
            self.evals.put((filename, result))
            self.data.task_done()
            #except queue.Empty:
                #break  # Exit if no more data is available

    def __next__(self):
        if self.evals.empty():
            raise StopIteration
        data = self.evals.get()
        self.evals.task_done()
        return data

    # def to_dcm(self, filename):
    #     '''
    #     Genrate from dataset DCM entres
    #     '''
    #     dcm = DCM(filename)
    #     dcm.params = self.dataset
    #     dcm.generate()

    # def to_cdf(self):
    #     pass

    # def csv(self):
    #     '''
    #     Write the data in csv file

    #     :return: None
    #     '''
    #     self.data.to_csv('%s.csv' % self.module)

    # def _pretty(self,data):
    #     logging.info("%s\n%s" %(self.module, tabulate(data,headers=data.columns,
    #    tablefmt="pretty")))

    # def _queued(self, q):
    #     while True:
    #         try:
    #             filename= q.get()
    #             q.task_done()
    #             self.set_file(filename)
    #             data=self.evaluate(self.get_data())
    #             self._pretty(data)
    #         except Exception as e:
    #             logging.error('%s' %str(e))

    # def worker(self,q):
    #     worker = Thread(target=self._queued, args=(q,))
    #     worker.setDaemon(True)
    #     worker.start()
    #     return worker
