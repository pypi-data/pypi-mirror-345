Here a simple script to enable/disable your NS.
This is the equiv of toggling the "Disable Alarms for Today" in the app.

::

    import os
    import json

    from ns_parental_controls import ParentalControl


    def save(**k):
        with open('test.json', 'wt') as file:
            file.write(json.dumps(k, indent=2))


    def load(**k):
        if not os.path.isfile('test.json'):
            return k

        try:
            with open('test.json', 'rt') as file:
                return json.load(file)
        except Exception as e:
            print(e)
            return k


    pc = ParentalControl(
        save_state_callback=save,
        load_state_callback=load,
        callback_kwargs={'random': 'kwargs'}
    )

    if not pc.access_token:
        if not pc.session_token:
            print(pc.get_auth_url())
            pc.process_auth_link(input('copy paste the button link "select this account" here:\n'))
        else:
            pc.get_new_access_token()

    # True means disable the NS
    # False means enable the NS
    pc.lock_device('My NS', False)
