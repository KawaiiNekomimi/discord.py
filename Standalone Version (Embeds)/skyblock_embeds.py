import asyncio
import datetime
import json
import os
import re
import time
import discord
import requests


def getendpointurl(key,name,profilename,endpoint):#APIｴﾝﾄﾞﾎﾟｲﾝﾄ取得関数。
    url = str("https://api.hypixel.net/player?key=" + (key) + "&name=" + (name))
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():#SBのｴﾝﾄﾞﾎﾟｲﾝﾄの取得にはﾌﾟﾛﾌｧｲﾙ名ではなくﾌﾟﾛﾌｧｲﾙIDっていうのを使うらしく二度手間()
        if (profs["cute_name"]) == profilename:
            url = str("https://api.hypixel.net/" + (endpoint)+  "?key=" + (key) + "&name=" + (name) + "&profile=" + str(profs["profile_id"]))
            return url
#Adapted to use Embeds by KawaiiNekomimi
def getmyauction(key, name, profilename):#MyClientｸﾗｽのon_messageで!ahｺﾏﾝﾄﾞが打たれたのを検知したら呼び出されます
    endpoint = "skyblock/auction"
    url = getendpointurl(key, name,profilename, endpoint)
    headers = {"content-type": "application/json"}
    r = requests.get(url, headers=headers)
    data = r.json()
    myauction = list(data["auctions"])#ここでまずｵｰｸｼｮﾝを全部洗い出し
    embed=discord.Embed(title="Auction House", color=0x00ff00)
    total_coins = 0
    for unclaimed in myauction:
        if (unclaimed["claimed"]) == False:#回収されていないものを選別
            item = str(unclaimed["item_name"])
            end = int(((unclaimed["end"])//1000)-time.time())#ﾊｲﾋﾟAPIでは時刻はUNIXｴﾎﾟｯｸ時間のﾐﾘ秒で提供されるので秒に揃えて現在の時間との差分を算出
            delta = datetime.timedelta(seconds=int(end))#UNIXｴﾎﾟｯｸ時間の単位は秒だから脳死割り算で日、時間、分を出せる便利
            deltam, deltas = divmod(delta.seconds, 60)#分
            deltah, deltam = divmod(deltam, 60)#時間
            deltad,deltah = divmod(deltah,24)#日
            highbid = "{:,}".format(int(unclaimed["highest_bid_amount"]))
            if end > 0:#ここからはbidの状態判定。まず終了しているかどうか
                embed.add_field(name=f":arrows_counterclockwise: Item: {item}", value=f"**Time Left**: {deltad}d {deltah}h {deltam}m {deltas}s\n**Highest bid**: {highbid} coins", inline=False)
                highbid = highbid.replace(",", "")
                total_coins = total_coins + int(highbid)
            else:
                if int(unclaimed["highest_bid_amount"]) == 0:#終了していればbidの有無を判定してそれぞれ出力するﾒｯｾｰｼﾞに入れ込みます
                    embed.add_field(name=f":warning: Item: {item}", value=f"**Time Left**: Ended\n**Highest bid**: No bids :(", inline=False)
                else:
                    embed.add_field(name=f":white_check_mark: Item: {item}", value=f"**Time Left**: Ended\n**Highest bid**: {highbid} coins", inline=False)
                    highbid = highbid.replace(",", "")
                    total_coins = total_coins + int(highbid)
    embed.add_field(name=":moneybag: Total Coins:", value="{:,}".format(int(total_coins)))
    return embed

def addnewusr(author,key,name,profilename):#新規ﾕｰｻﾞｰ追加
    path_name = str(os.path.dirname(os.path.abspath(__file__)))
    newfile = f"{path_name}/usrdata/"+(author)+".json"#DiscordのﾕﾆｰｸIDをﾌｧｲﾙ名にしてAPIｷｰ、MCID、ﾌﾟﾛﾌｧｲﾙ名をjson格納という至ってｼﾝﾌﾟﾙな管理なんだけど、これだとﾏﾙﾁﾌﾟﾛﾌｧｲﾙに対応できない悲しみ
    with open(newfile, "w") as nf:
        data = {"key": str(key), "name": str(name), "profile": str(profilename)}
        json.dump(data, nf, ensure_ascii=False)
    f = open(newfile)
    newusr = json.load(f)
    key = str(newusr["key"])
    name = str(newusr["name"])
    profile = str(newusr["profile"])
    f.close()
    return key, name, profile#登録情報を確認するために書き込んだ情報をreturnします

class MyClient(discord.Client):

    async def on_ready(self):#ここにｹﾞｰﾑ内ｲﾍﾞﾝﾄの通知機能を入れ込む予定
        return

    async def on_message(self, message):#ﾒｯｾｰｼﾞ監視
        if message.author == self.user:
            return

        if re.compile("!ah").match(message.content):#ｺﾏﾝﾄﾞを検知
            author = str(message.author.id)#ﾕｰｻﾞｰのﾕﾆｰｸIDを取得
            path_name = str(os.path.dirname(os.path.abspath(__file__)))
            try:#登録情報を確認します
                usrdata = f"{path_name}/usrdata/"+(author)+".json"
                f = open(usrdata)
                usr = json.load(f)
                key = str(usr["key"])
                name = str(usr["name"])
                profilename = str(usr["profile"])
                getmyauction(key, name, profilename)
                embed = getmyauction(key, name, profilename))
                await message.channel.send(embed=embed)
            except KeyError:#正しく登録されてるはずなのになぜか出るｷｰｴﾗｰ禿げる
                await message.channel.send(f"{message.author.mention}\n:warning: Key Error\nAPI key is invalid. Please use `!add (API key) (MCID) (profile name)` again")
            except FileNotFoundError:#FileNotFoundErrorと未登録を安易に同値とできるあたりこの管理形式は天才だと思った(小並
                await message.channel.send(f"{message.author.mention}\nYou haven't registered your API key yet\nYou can use `!add (API key) (MCID) (profile name)` to register\n\nAPI key can be obtained in-game with `/api` or `/api new`")
            return

        if re.compile("(!add )(.+)( |,)(.+)( |,)(.+)").match(message.content):#!addｺﾏﾝﾄﾞで打たれた内容を切り分けて登録する。単純な正規表現です。
            author = str(message.author.id)
            com = re.match("(!add )(.+)( |,)(.+)( |,)(.+)", message.content)
            key = com.group(2)
            name = com.group(4)
            profilename = com.group(6)
            newkey,newname,newprofile = addnewusr(author,key,name,profilename)
            await message.channel.send(f"{message.author.mention} Registration complete.\nKey: {newkey}\nMCID: {newname}\nProfile: {newprofile}")
            return
            

client = MyClient()
token = ("TOKEN")
client.run(token)
