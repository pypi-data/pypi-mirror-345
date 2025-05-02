=====
Usage
=====

To use rey in a project::

    import rey

Basic Usage
----------

Here's an example of basic usage::

    from rey import example

    # Use the hello function
    greeting = example.hello("User")
    print(greeting)  # Outputs: Hello, User!

    # Create an Example class instance
    ex = example.Example("test value")
    print(ex.get_value())  # Outputs: test value
