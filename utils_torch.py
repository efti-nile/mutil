def print_last_layers(model, n_layers):
    named_params = dict(model.named_parameters())
    names = list(named_params.keys())
    for name in names[-n_layers:]:
        print(name)


def unfreeze_last_layers(model, n_layers):
    named_params = dict(model.named_parameters())
    names = list(named_params.keys())
    for name in names[-n_layers:]:
        named_params[name].requires_grad = True


def freeze_all_layers(model):
    for p in model.parameters():
        p.requires_grad = False

        