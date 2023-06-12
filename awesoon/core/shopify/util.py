import html


def decode_html_policies(policies):
    decoded_policies = []
    for policy in policies:
        if policy["body"]:
            decoded_policies.append(html.unescape(policy["body"]))
    return decoded_policies
