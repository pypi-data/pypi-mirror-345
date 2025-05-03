try:
    from opensees.openseespy import Model
except:
    import warnings
    warnings.warn("Failed to import OpenSees bindings")
    Model = None

