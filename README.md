# Crypto Pump-and-Dump Bot

Automatically scrapes Discord Crypto Pump and Dump channels and long/short the specified coined asap once announced

---

## Disclaimer

This project is for informational purposes only. You should not construe any such information or other material as
legal, tax, investment, financial, or other advice. Nothing contained here constitutes a solicitation, recommendation,
endorsement, or offer by me or any third party service provider to buy or sell any securities or other financial
instruments in this or in any other jurisdiction in which such solicitation or offer would be unlawful under the
securities laws of such jurisdiction.

If you plan to use real money, USE AT YOUR OWN RISK.

Under no circumstances will I be held responsible or liable in any way for any claims, damages, losses, expenses, costs,
or liabilities whatsoever, including, without limitation, any direct or indirect damages for loss of profits.

## Background

There have been lots of crypto pump-and-dump (PND) schemes on lesser-known altcoins. How they work can typically be
concluded in a paper written by Jiahua Xu and Benjamin Livshits, The Anatomy of a Cryptocurrency Pump-and-Dump Scheme (
DOI:10.2139/ssrn.3303365).

> Set-up: The organizer creates a publicly accessible group or channel, and recruits as many group members or channel
> sub- scribers as possible by advertising and posting invitation links on major forums such as Bitcointalk, Steemit, and
> Reddit.
>
> Telegram channels only allow subscribers to receive mes- sages from the channel admin, but not post discussions in the
> channel. In a Telegram group, members can by default post messages, but this function is usually disabled by the group
> admin to prohibit members’ interference. We use the terms channel and group interchangeably in this paper.
>
> Pre-pump announcement: The group is ready to pump once it obtains enough members (typically above 1,000). The pump
> organizer, who is now the group or channel admin, announces details of the next pump a few days ahead. The admins broad-
> cast the exact time and date of the announcement of a coin which would then precipitate a pump of that coin. Other in-
> formation disclosed in advance includes the exchange where the pump will take place and the pairing coin2. The admins
> advise members to transfer sufficient funds (in the form of the pairing coin) into the named exchange beforehand.
>
> While the named pump time is approaching, the admin sends out countdowns, and repeats the pump “rules” such as: 1) buy
> fast, 2) “shill”3 the pumped coin on the exchange chat box and social media to attract outsiders, 3) “HODL”4 the coin at
> least for several minutes to give outsiders time to join in, 4) sell in pieces and not in a single chunk, 5) only sell
> at a profit and never sell below the current price. The admin also gives members a pep talk, quoting historical pump
> profits, to boost members’ confidence and encourage their participation.
>
> Pump: At the pre-arranged pump time, the admin announces the coin, typically in the format of an OCR (optical
> character recognition)-proof image to hinder machine reading (Fig- ure 1). Immediately afterwards, the admin urges
> members to buy and hold the coin in order to inflate the coin price. During the first minute of the pump, the coin price
> surges, sometimes increasing several fold.
>
> Dump: A few minutes (sometimes tens of seconds) after the pump starts, the coin price will reach its peak. While the
> admin might shout “buy buy buy” and “hold hold hold” in the channel, the coin price keeps dropping. As soon as the first
> fall in price appears, pump-and-dump participants start to panic-sell. While the price might be re-boosted by the second
> wave of purchasers who buy the dips (as encouraged by channel admins), chances are the price will rapidly bounce back to
> the start price, sometimes even lower. The coin price declining to the pre-pump proximity also signifies the end of the
> dump, since most investors would rather hold the coin than sell at a loss.
>
> Post-pump review: Within half an hour, after the coin price and trading volume recover to approximately the pre-pump
> levels, the admin posts a review on coin price change, typi- cally including only two price points — start price (or low
> price) and peak price, and touts how much the coin price in-creased by the pump (Figure 1). Information such as trading
> volume and timescale is only selectively revealed: if the vol- ume is high, and the pump-and-dump lasts a long time (
> over 10 minutes, say, would be considered “long”), then those stats will be “proudly” announced; if the volume is low or
> the time between coin announcement and price peak is too short (which is often the case), then the information is
> glossed over. Such posts give newcomers, who can access channel history, the illusion that pump-and-dumps are highly
> profitable.

In a nutshell, PND organizers create and advertise public online text channel/group on platforms such as Discord and
Telegram. They announce a scheduled PND without but only reveal the coin to be PND-ed. After the announcement of the
symbol the altcoin spikes to an average 150%-300%, then shortly returns to the original price or even lower.

This program listens to Discord messages such that when it detects a coin symbol within the text, it instantly buys the
coin and quickly sells it back after the price has been increased to a predefined percentage (+20% by default.)

## Usage

Create a Discord account, a Binance account with API token and find the target Discord PND channel.

Change the Regex expression which captures the altcoin ticker symbol at `discord_scraper.py`.

Create a `.env` file with the syntax defined as `.env.sample`.

```
DISCORD_EMAIL=*****
DISCORD_PASSWORD=*****
PND_CHANNEL_URL=https://discord.com/channels/*****/*****
BINANCE_API_KEY=*****
BINANCE_API_SECRET=*****
```

Execute the following command to start listening to the Discord channel.

```shell
python3 main.py
```