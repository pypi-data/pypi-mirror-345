import re
from asyncio import run, sleep
from enum import StrEnum
from os.path import dirname
from typing import Literal

from aiogram.types import BufferedInputFile
from playwright.async_api import async_playwright, Page
from pyotp import TOTP
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from playwright._impl._errors import TimeoutError
from xync_schema.enums import UserStatus
from xync_schema.models import User, PmAgent

from xync_client.TgWallet.pyro import PyroClient
from xync_client.loader import bot


class ExtraCaptchaException(Exception): ...


class Pages(StrEnum):
    base_url = "https://account.volet.com/"
    LOGIN = base_url + "login"
    OTP = base_url + "login/otp"
    HOME = base_url + "pages/transaction"
    SEND = base_url + "pages/transfer/wallet"
    GMH = "https://mail.google.com/mail/u/0/"


def parse_transaction_info(text: str) -> dict[str, str] | None:
    # Поиск ID транзакции
    transaction_id_match = re.search(r"Transaction ID:\s*([\w-]+)", text)
    # Поиск суммы и валюты
    amount_match = re.search(r"Amount:\s*([+-]?[0-9]*\.?[0-9]+)\s*([A-Z]+)", text)
    # Поиск email отправителя
    sender_email_match = re.search(r"Sender:\s*([\w.-]+@[\w.-]+)", text)

    if transaction_id_match and amount_match and sender_email_match:
        return {
            "transaction_id": transaction_id_match.group(1),
            "amount": amount_match.group(1),
            "currency": amount_match.group(2),
            "sender_email": sender_email_match.group(1),
        }
    return None


async def report(uid: int, byts: bytes, msg: str, exc: bool = True):
    infile = BufferedInputFile(byts, msg)
    await bot.send_photo(uid, infile, caption=msg)
    if exc:
        raise Exception(msg)


class Client:
    agent: PmAgent
    pbot: PyroClient
    page: Page
    gpage: Page

    msgs: dict = {}
    msg_listener: MessageHandler

    def __init__(self, uid: int):
        self.uid = uid

    async def start(self, headed: bool = False):
        self.agent = await PmAgent.get(user_id=self.uid, user__status__gt=0, pm__norm="volet").prefetch_related("user")

        self.pbot = PyroClient(self.agent)
        await self.pbot.app.start()
        self.msg_listener = MessageHandler(self.got_msg, filters.chat(["ProtectimusBot"]))
        self.pbot.app.add_handler(self.msg_listener)

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            channel="chrome",
            headless=not headed,
            timeout=5000,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-infobars",
                "--disable-extensions",
                "--start-maximized",
            ],
        )
        context = await browser.new_context(storage_state=self.agent.auth.get("state", {}), locale="en")
        context.set_default_navigation_timeout(15000)
        context.set_default_timeout(12000)
        self.page = await context.new_page()

        await self.gmail_page()
        await self.go(Pages.HOME)
        if self.page.url == Pages.LOGIN:
            await self.login()
        if self.page.url != Pages.HOME:
            await report(self.uid, await self.page.screenshot(), "Not logged in!")

    async def login(self):
        await self.page.locator("input#j_username").fill("mixartemev@gmail.com")
        await self.page.locator("input#j_password").fill("mixfixX98")
        await self.page.locator("input#loginToAdvcashButton", has_text="log in").hover()
        await self.page.locator("input#loginToAdvcashButton:not([disabled])", has_text="log in").click()
        code = await self.wait_for_code("login")
        if not code:
            await report(self.uid, await self.page.screenshot(), "no login code")
        await self.page.locator("input#otpId").fill(code)
        await self.page.click("input#checkOtpButton")
        await self.page.wait_for_url(Pages.HOME)

    async def wait_for_code(self, typ: Literal["login", "send"], past: int = 0, timeout: int = 5) -> str:
        while past < timeout:
            if code := self.msgs.pop(f"otp_{typ}", None):
                return code
            await sleep(1)
            past += 1
            return await self.wait_for_code(typ, past)

    async def got_msg(self, _, msg: Message):
        if "Your OTP code:" in msg.text:
            self.msgs["otp_login"] = msg.text[-6:]
        if "Confirmation code:" in msg.text:
            self.msgs["otp_send"] = msg.text[-6:]
        elif "Status: Completed. Sender:" in msg.text:
            self.msgs["got_payment"] = parse_transaction_info(msg.text)

    async def send(self, dest: str, amount: float):
        await self.go(Pages.SEND)
        await self.page.click("[class=combobox-account]")
        await self.page.click('[class=rf-ulst-itm] b:has-text("Ruble ")')
        await self.page.wait_for_timeout(200)
        await self.page.fill("#srcAmount", str(amount))
        await self.page.fill("#destWalletId", dest)
        await self.page.wait_for_timeout(300)
        await self.page.locator("input[type=submit]", has_text="continue").click()
        if otp := self.agent.auth.get("otp"):
            totp = TOTP(otp)
            code = totp.now()
        elif self.agent.auth.get("sess"):
            if not (code := await self.wait_for_code("send")):  # todo: why no get code?
                await self.mail_confirm()
        else:
            raise Exception(f"PmAgent {self.uid} has No OTP data")
        if not code:
            await report(self.uid, await self.page.screenshot(), "no send code")
        await self.page.fill("#securityValue", code)
        await self.page.locator("input[type=submit]", has_text="confirm").click()
        await self.page.wait_for_url(Pages.SEND)
        await self.page.get_by_role("heading").click()
        slip = await self.page.screenshot(clip={"x": 440, "y": 205, "width": 420, "height": 360})
        await report(self.uid, slip, f"{amount} to {dest} sent", False)

    async def gmail_page(self):
        gp = await self.page.context.new_page()
        await gp.goto(Pages.GMH, timeout=20000)
        if not gp.url.startswith(Pages.GMH):
            # ваще с 0 заходим
            if await (
                sgn_btn := gp.locator(
                    'header a[href^="https://accounts.google.com/AccountChooser/signinchooser"]:visible',
                    has_text="sign in",
                )
            ).count():
                await sgn_btn.click()
            # если надо выбрать акк
            lang = await gp.get_attribute("html", "lang")
            sgn = {
                "ru": "Выберите аккаунт",
                "en": "Choose an account",
            }
            if await gp.locator("h1#headingText", has_text=sgn[lang]).count():
                await gp.locator("li").first.click()
            # если предлагает залогиниться
            elif await gp.locator("h1#headingText", has_text="Sign In").count():
                await gp.fill("input[type=email]", self.agent.user.gmail_auth["login"])
                await gp.locator("button", has_text="Next").click()
            # осталось ввести пороль:
            await gp.fill("input[type=password]", self.agent.user.gmail_auth["password"])
            nxt = {"ru": "Далее", "en": "Next"}
            await gp.locator("button", has_text=nxt[lang]).click()
            await report(self.uid, await gp.screenshot(), "Аппрувни гмейл, у тебя 1.5 минуты", False)
        await gp.wait_for_url(lambda u: u.startswith(Pages.GMH), timeout=90 * 1000)  # убеждаемся что мы в почте
        self.gpage = gp

    async def mail_confirm(self):
        lang = await self.gpage.get_attribute("html", "lang")
        labs = {
            "ru": "Оповещения",
            "en-US": "Updates",
        }
        tab = self.gpage.get_by_role("heading").get_by_label(labs[lang]).last
        await tab.click()
        rows = self.gpage.locator("tbody>>nth=4 >> tr")
        row = rows.get_by_text("Volet.com").and_(rows.get_by_text("Please Confirm Withdrawal"))
        if not await row.count():
            await report(self.uid, await self.gpage.screenshot(), "А нет запросов от волета")
        await row.click()
        await self.gpage.wait_for_load_state()
        btn = self.gpage.locator('a[href^="https://account.volet.com/verify/"]', has_text="confirm").first
        await btn.click()

    async def go(self, url: Pages):
        try:
            await self.page.goto(url)
            if len(await self.page.content()) < 1000:  # todo: fix captcha symptom
                await self.captcha_click()
        except Exception as e:
            await report(self.uid, await self.page.screenshot(), repr(e))

    async def captcha_click(self):
        captcha_url = self.page.url
        cbx = self.page.frame_locator("#main-iframe").frame_locator("iframe").first.locator("div#checkbox")
        await cbx.wait_for(state="visible"), await self.page.wait_for_timeout(500)
        await cbx.click(delay=94)
        try:
            await self.page.wait_for_url(lambda url: url != captcha_url)
        except TimeoutError:  # if page no changed -> captcha is undone
            await self.page.screenshot(path=dirname(__file__) + "/xtr_captcha.png")
            raise ExtraCaptchaException(self.page.url)

    async def wait_for_payments(self, interval: int = 29):
        while (await User[self.uid]).status > UserStatus.SLEEP:
            await self.page.reload()
            await self.page.wait_for_timeout(interval * 1000)

    async def stop(self):
        # save state
        if state := await self.page.context.storage_state():
            self.agent.auth["state"] = state
            await self.agent.save()
        # closing
        await self.page.context.close()
        await self.page.context.browser.close()
        self.pbot.app.remove_handler(self.msg_listener)
        await self.pbot.app.stop()


async def _test(uid: int, dest: str, amount):
    from x_model import init_db
    from xync_client.loader import PG_DSN
    from xync_schema import models

    _ = await init_db(PG_DSN, models, True)
    va = Client(uid)
    try:
        await va.start(True)
        await va.send(dest, amount)
        await va.wait_for_payments()
    except TimeoutError as te:
        await report(uid, await va.page.screenshot(), repr(te))
    await va.stop()


if __name__ == "__main__":
    run(_test(7807393311, "alena.artemeva25@gmail.com", 8.3456))
