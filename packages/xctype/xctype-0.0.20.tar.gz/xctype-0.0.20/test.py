import test
import xctype

if __name__ == '__main__':
    import logging

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    logformat = '%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s'
    logdatefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level='DEBUG', format=logformat, datefmt=logdatefmt)
    test.test()
