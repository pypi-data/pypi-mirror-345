class ELTPipeline:
    def __init__(self, extractor, transformer, loader):
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self, extract_method, extract_args,
                  transform_steps, load_method, load_args):
        # Step 1: Extract
        data = extract_method(*extract_args)

        # Step 2: Transform
        for step in transform_steps:
            data = step(data)

        # Step 3: Load
        load_method(data, *load_args)
        
        
        
