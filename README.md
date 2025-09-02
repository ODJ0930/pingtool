# pingtool

A simple CLI tool to ping IP addresses grouped by country and report average latency and packet loss.

## Usage

```bash
python pingtool.py --country cn
```

## One-click from GitHub

Run the tool without cloning the repository:

```bash
bash <(curl -sSL https://raw.githubusercontent.com/<yourname>/pingtool/main/pingtool.sh) --country cn
```

You can provide ISO codes, English names, or certain Chinese country names (e.g., `中国` for China).

The tool will download the [public-dns.info](https://public-dns.info/) dataset on first run. If the network is unavailable, a small sample dataset in `data/nameservers.sample.json` will be used instead.

Use `--count` to limit the number of IPs per country and `--packets` to control the number of ping packets.

## Example

```bash
python pingtool.py --country 中国 --count 2 --packets 2
```
