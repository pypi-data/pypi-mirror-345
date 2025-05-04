import pytest
from unittest import mock

from powerline_diskspace.diskspace import get_disk_usage, DiskspaceSegment


@pytest.fixture(name="linux_df_output")
def _linux_df_output() -> str:
    return """
Filesystem                      Type      1K-blocks       Used Available Use% Mounted on
udev                            devtmpfs   65145048          0  65145048   0% /dev
tmpfs                           tmpfs      13050996       2364  13048632   1% /run
/dev/mapper/ubuntu_vg-ubuntu_lv ext4      981825020  412155452 519721920  45% /
tmpfs                           tmpfs      65254960        604  65254356   1% /dev/shm
tmpfs                           tmpfs          5120          0      5120   0% /run/lock
tmpfs                           tmpfs      65254960          0  65254960   0% /sys/fs/cgroup
/dev/sda2                       ext4         996780     479424    448544  52% /boot
/dev/loop1                      squashfs      57088      57088         0 100% /snap/core00/0000
/dev/sdc2                       ext4      983378676  317243540 616108572  34% /cache
/dev/sdb                        ext4     1921725720 1039417596 784616012  57% /scratch2
/dev/loop4                      squashfs      65536      65536         0 100% /snap/core20/1169
/dev/loop5                      squashfs      39680      39680         0 100% /snap/snapd/12345
tmpfs                           tmpfs      13050992          0  13050992   0% /run/user/1001
    """.strip()


def test_diskspace_nominal(linux_df_output):
    res = get_disk_usage(linux_df_output)
    sample = res[1]
    assert sample == {
        "filesystem": "tmpfs",
        "type": "tmpfs",
        "blocks": 13050996,
        "used": 2364,
        "available": 13048632,
        "total": 13050996,
        "capacity": 1.0,
        "mounted_on": "/run",
    }


def test_disk_space_segment_nominal(linux_df_output: str):
    seg = DiskspaceSegment()
    with mock.patch(
        "powerline_diskspace.diskspace.get_df_output"
    ) as mock_get_df_output:
        mock_get_df_output.return_value = linux_df_output

        res_v0 = seg(
            None,
            None,
            None,
            "{mounted_on} {capacity}",
            mount_ignore_pattern="/dev",
            update_rate_s=0.0,
            show_when_used_over_percent={"/": 0.0},
        )
        assert len(res_v0) == 11

        assert res_v0[0]["contents"] == "/run 1.0"
        assert res_v0[0]["highlight_groups"] == ["information:additional"]

        assert res_v0[5]["highlight_groups"] == ["critical:failure"]
