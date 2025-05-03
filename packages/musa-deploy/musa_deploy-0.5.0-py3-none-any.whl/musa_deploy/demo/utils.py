from musa_deploy.utils import shell_cmd


def get_IP_address():
    out, _, _ = shell_cmd.run_cmd("hostname -I | awk '{print $1}'")
    return out


if __name__ == "__main__":
    print(get_IP_address())
