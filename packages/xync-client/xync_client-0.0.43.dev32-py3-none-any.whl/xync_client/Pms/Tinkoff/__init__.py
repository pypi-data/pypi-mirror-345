import asyncio
import os
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="state.json")
        if session_storage := os.environ.get("SESSION_STORAGE"):
            await context.add_init_script(
                """(storage => {
              if (window.location.hostname === 'example.com') {
                const entries = JSON.parse(storage)
                for (const [key, value] of Object.entries(entries)) {
                  window.sessionStorage.setItem(key, value)
                }
              }
            })('"""
                + session_storage
                + "')"
            )
        page = await context.new_page()
        await page.goto("https://www.tbank.ru/mybank/")
        await page.wait_for_timeout(3000)
        try:
            await page.wait_for_url("https://www.tbank.ru/mybank/", timeout=3000)
        except TimeoutError:
            # Новый пользователь
            if await page.locator('[automation-id="form-title"]', has_text="Вход в Т‑Банк").is_visible():
                await page.wait_for_timeout(500)
                await page.locator('[automation-id="phone-input"]').fill("9992259898")
                await page.locator('[automation-id="button-submit"] svg').click()
            # Известный пользователь
            else:
                await page.locator('[automation-id="button-submit"]').click()
                await page.wait_for_timeout(300)
            await page.locator('[automation-id="otp-input"]').fill(input("Введите код"))
            if await page.locator('[automation-id="cancel-button"]').is_visible():
                await page.locator('[automation-id="cancel-button"]').click()
            await page.context.storage_state(path="state.json")
            session_storage = await page.evaluate("() => JSON.stringify(sessionStorage)")
            os.environ["SESSION_STORAGE"] = session_storage
        # Переходим на сбп и вводим данные получателя
        await page.locator(
            '[data-qa-type="desktop-ib-pay-buttons"] [data-qa-type="atomPanel pay-card-0"]',
            has_text="Перевести по телефону",
        ).click()
        await page.locator('[data-qa-type="recipient-input.value.placeholder"]').click()
        await page.wait_for_timeout(300)
        await page.locator('[data-qa-type="recipient-input.value.input"]').fill("9992259898")
        await page.locator('[data-qa-type="amount-from.placeholder"]').click()
        await page.locator('[data-qa-type="amount-from.input"]').fill("100")
        await page.wait_for_timeout(300)
        await page.locator('[data-qa-type="bank-plate-other-bank click-area"]').click()
        await page.locator('[data-qa-type*="inputAutocomplete.value.input"]').click()
        await page.locator('[data-qa-type*="inputAutocomplete.value.input"]').fill("Озон")
        await page.wait_for_timeout(300)
        await page.locator('[data-qa-type="banks-popup-list"]').click()
        await page.locator('[data-qa-type="transfer-button"]').click()

        # Проверка последнего платежа
        await page.goto("https://www.tbank.ru/events/feed")
        await page.wait_for_timeout(500)
        try:
            for am in await page.locator('[data-qa-type="timeline-operations-list"] [data-qa-type="operation-money"]'):
                if float(am) < 0:
                    continue
                else:
                    await page.locator(
                        '[data-qa-type="timeline-operations-list"] [data-qa-type="operation-title"] >> nth=0'
                    ).text_content()  # проверка имени отправителя
                    amount = await page.locator(
                        '[data-qa-type="timeline-operations-list"] [data-qa-type="operation-money"] >> nth=0'
                    ).text_content()  # проверка суммы
                    amount = round(float(amount))
        except TimeoutError:
            await page.locator(
                '[data-qa-type="timeline-operations-list"] [data-qa-type="operation-title"] >> nth=1'
            ).text_content()  # проверка имени отправителя
            amount = await page.locator(
                '[data-qa-type="timeline-operations-list"] [data-qa-type="operation-money"] >> nth=1'
            ).text_content()  # проверка суммы
            amount = round(float(amount))
    await browser.close()


asyncio.run(main())
