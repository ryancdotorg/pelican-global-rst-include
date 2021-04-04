import os
import docutils
from pelican import signals

def process_settings(instance):
    files = instance.settings.get('RST_GLOBAL_INCLUDES', []) or []

    if len(files) > 0:
        base = instance.settings.get('PATH', '.')

        def include(filename):
            with open(os.path.join(base, filename), 'r') as res:
                return f'.. included from `{filename}`\n{res.read()}\n'

        # load all the files
        prepend = ''.join(map(include, files))

        class SourcePrepender:
            def __init__(self, source):
                self.source = source

            def read(self):
                return prepend + self.source.read()

            def close(self):
                self.source.close()

        class PrependedFileInput(docutils.io.FileInput):
            def __init__(self, *args, **kwargs):
                docutils.io.FileInput.__init__(self, *args, **kwargs)
                if kwargs['source_path'].endswith('.rst'):
                    self.source = SourcePrepender(self.source)

        # save reference to original function
        _set_source = docutils.core.Publisher.set_source
        # our wrapper around that function
        def set_source(self, source=None, source_path=None):
            self.source_class = PrependedFileInput
            return _set_source(self, source, source_path)
        # monkey patch the wrapper into docutils
        docutils.core.Publisher.set_source = set_source

def register():
    signals.initialized.connect(process_settings)
