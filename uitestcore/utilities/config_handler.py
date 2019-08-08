def parse_config_data(context):
    """
    Set any relevant config items on the context
    :param context: the test context instance
    """
    if context.config.userdata:

        for key, value in context.config.userdata.items():

            if key.lower() == 'base_url':
                context.url = value
                continue

            elif key.lower() == "logging_flag":

                if value.lower() == "false":
                    context.logging_flag = False
                    continue

                else:
                    context.logging_flag = True
                    continue

            elif key.lower() == "maximize_browser_flag":

                if value.lower() == "false":
                    context.maximize_browser = False
                    continue

                else:
                    context.maximize_browser = True
                    continue

            elif key.lower() == "browser":
                context.browser = value

    else:
        print("No Command line Params detected, using Config file values")
