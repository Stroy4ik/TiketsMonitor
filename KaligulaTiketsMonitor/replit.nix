{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.nodejs
    pkgs.playwright-driver
    pkgs.chromium
  ];
}
