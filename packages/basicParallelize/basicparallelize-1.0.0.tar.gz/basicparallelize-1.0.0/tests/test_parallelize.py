import unittest

from parallelize import multiThread
from parallelize import multiThreadTQDM
from parallelize import parallelProcess
from parallelize import parallelProcessTQDM


def oneArgFunction(x):
    return x**2


def twoArgFunction(x, y):
    return x + y


class TestParallelize(unittest.TestCase):
    """Test output equivalency of multithreading and parallel processing to the results of serial execution of a function.
    Known Failure States:
        TypeError: Attempting to pass an incorrect number of arguments to a function.
        AttrributeError: Attempting to pass a local function to a process pool.
    """

    def setUp(self):
        self.argsOneArgFunction = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.argsTwoArgFunction = [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
        ]

    def tearDown(self):
        del self.argsOneArgFunction
        del self.argsTwoArgFunction

    def testMultiThreadOneArg(self):
        self.assertEqual(
            multiThread(oneArgFunction, self.argsOneArgFunction),
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
        )

    def testMultiThreadTwoArgs(self):
        self.assertEqual(
            multiThread(twoArgFunction, self.argsTwoArgFunction),
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        )

    def testMultiThreadTQDMOneArg(self):
        self.assertEqual(
            multiThreadTQDM(oneArgFunction, self.argsOneArgFunction),
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
        )

    def testMultiThreadTQDMTwoArgs(self):
        self.assertEqual(
            multiThreadTQDM(twoArgFunction, self.argsTwoArgFunction),
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        )

    def testParallelProcessOneArg(self):
        self.assertEqual(
            parallelProcess(oneArgFunction, self.argsOneArgFunction),
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
        )

    def testParallelProcessTwoArgs(self):
        self.assertEqual(
            parallelProcess(twoArgFunction, self.argsTwoArgFunction),
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        )

    def testParallelProcessTQDMOneArg(self):
        self.assertEqual(
            parallelProcessTQDM(oneArgFunction, self.argsOneArgFunction),
            [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
        )

    def testParallelProcessTQDMTwoArgs(self):
        self.assertEqual(
            parallelProcessTQDM(twoArgFunction, self.argsTwoArgFunction),
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        )

    def testKnownFailureStates(self):
        # Local functions for failure testing
        def localOneArgFunction(x):
            return x**2

        def localTwoArgFunction(x, y):
            return x + y

        # Confirm that attempting to map two arguments to a one argument function fails
        with self.assertRaises(TypeError):
            multiThread(oneArgFunction, self.argsTwoArgFunction)
        # Confirm that threads can handle local functions
        multiThread(localOneArgFunction, self.argsOneArgFunction)
        # Confirm that attempting to map one argument to a two argument function fails
        with self.assertRaises(TypeError):
            multiThread(twoArgFunction, self.argsOneArgFunction)
        # Confirm that threads can handle local functions
        multiThread(localTwoArgFunction, self.argsTwoArgFunction)
        # Confirm that attempting to map two arguments to a one argument function fails
        with self.assertRaises(TypeError):
            multiThreadTQDM(oneArgFunction, self.argsTwoArgFunction)
        # Confirm that threads can handle local functions
        multiThreadTQDM(localOneArgFunction, self.argsOneArgFunction)
        # Confirm that attempting to map one argument to a two argument function fails
        with self.assertRaises(TypeError):
            multiThreadTQDM(twoArgFunction, self.argsOneArgFunction)
        # Confirm that threads can handle local functions
        multiThreadTQDM(localTwoArgFunction, self.argsTwoArgFunction)
        # Confirm that attempting to map two arguments to a one argument function fails
        with self.assertRaises(TypeError):
            parallelProcess(oneArgFunction, self.argsTwoArgFunction)
        # Confirm that using a local function fails for processes
        with self.assertRaises(AttributeError):
            parallelProcess(localOneArgFunction, self.argsOneArgFunction)
        # Confirm that attempting to map one argument to a two argument function fails
        with self.assertRaises(TypeError):
            parallelProcess(twoArgFunction, self.argsOneArgFunction)
        # Confirm that using a local function fails for processes
        with self.assertRaises(AttributeError):
            parallelProcess(localTwoArgFunction, self.argsTwoArgFunction)
        # Confirm that attempting to map one argument to a two argument function fails
        with self.assertRaises(TypeError):
            parallelProcessTQDM(twoArgFunction, self.argsOneArgFunction)
        # Confirm that using a local function fails for processes
        with self.assertRaises(AttributeError):
            parallelProcessTQDM(localTwoArgFunction, self.argsTwoArgFunction)
        # Confirm that attempting to map two arguments to a one argument function fails
        with self.assertRaises(TypeError):
            parallelProcessTQDM(oneArgFunction, self.argsTwoArgFunction)
        # Confirm that using a local function fails for processes
        with self.assertRaises(AttributeError):
            parallelProcessTQDM(localOneArgFunction, self.argsOneArgFunction)


if __name__ == "__main__":
    unittest.main(verbosity=0)
