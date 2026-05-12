from __future__ import annotations


def print_header(title: str) -> None:
    label = f" {title} ====="
    print(label.rjust(80, "="))


def print_subheader(subtitle: str) -> None:
    label = f" {subtitle} -----"
    print(label.rjust(80, "-"))
