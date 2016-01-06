from stacktraces import python_traceback, process_model


def describe_lines(traceback_lines):
    p = process_model.Process(0)
    ptb = python_traceback.PythonTraceback(
        proc=p, lines=traceback_lines, name='Python Exception'
    )
    ptb.parse()
    # thread_analyzer.cleanup(p, my_cleanups)
    # thread_analyzer.annotate(p, my_annotations)
    p.group()  # only one thread, but this allows str(p) to work
    return unicode(p)
