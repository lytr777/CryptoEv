from util.generator import generate_key


def create_init_case(cnf, algorithm):
    parameters = {"secret_key": generate_key(algorithm.secret_key_len)}
    return create_case(cnf, parameters, algorithm)


def create_case(cnf, parameters, algorithm):
    case = algorithm(cnf)

    if "key_stream" in parameters:
        case.set_key_stream(parameters["key_stream"])

    if "secret_key" in parameters:
        if "secret_mask" in parameters:
            case.set_secret_key(parameters["secret_key"], parameters["secret_mask"])
        else:
            case.set_secret_key(parameters["secret_key"])

    return case
