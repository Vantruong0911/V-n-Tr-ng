import asyncio
import time
from playwright.async_api import async_playwright

TARGET_VIDEO_URL = "https://vt.tiktok.com/ZSg77qgAd/"
SERVICE_NAME = "Hearts"  # Options: Hearts, Views, Shares, Favorites

async def solve_captcha_wait(page):
    print("[*] Đang chờ trang web tải CAPTCHA...")
    await asyncio.sleep(5)
    
    while True:
        try:
            # Kiểm tra xem đã vào được màn hình chính chưa
            if await page.locator("div.row button").first.is_visible():
                print("[+] Đã vượt CAPTCHA thành công!")
                break
        except Exception:
            pass

        # Chụp ảnh màn hình để xem mã CAPTCHA
        await page.screenshot(path="captcha.png")
        print("[!] Đã lưu ảnh 'captcha.png'. Hãy mở file ảnh này trong Explorer để xem chữ!")
        
        # Nhập mã CAPTCHA ngay tại Terminal
        captcha_text = input(">>> Nhập chữ CAPTCHA trong ảnh vào đây rồi bấm Enter: ")
        
        try:
            # Điền chữ vào ô trống và nhấn Enter
            inp = page.locator("input[type='text'], input[placeholder*='word']").first
            await inp.fill(captcha_text.strip())
            await inp.press("Enter")
            print("[*] Đang kiểm tra kết quả, vui lòng đợi 5 giây...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[-] Lỗi khi điền CAPTCHA (hãy xem lại ảnh captcha.png): {e}")

async def run_heart_loop(video_url: str, service: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.goto("https://zefoy.com/", wait_until="domcontentloaded")

        await solve_captcha_wait(page)

        # Locate the target service card and click its button
        service_btn = page.locator(f"//h5[contains(text(), '{service}')]/following-sibling::button[not(@disabled)]")
        if await service_btn.count() == 0:
            print(f"[-] Service '{service}' is currently offline on panel.")
            await browser.close()
            return
        await service_btn.first.click()

        # Locate active visible input box
        input_box = page.locator("div.col-sm-5 input[type='search']:visible")
        await input_box.fill(video_url)

        search_btn = page.locator("div.col-sm-5 button[type='submit']:visible")

        cycles = 0
        while True:
            try:
                await search_btn.click()
                await asyncio.sleep(3)

                # Check if cooldown timer is active
                timer_text = await page.locator("span.br.seconds:visible, h4:visible").all_inner_texts()
                send_btn = page.locator("div.col-sm-5 button.btn-dark:visible, button.wbutton:visible")

                if await send_btn.count() > 0:
                    await send_btn.first.click()
                    cycles += 1
                    print(f"[+] Cycle {cycles}: Dispatched {service} batch -> {video_url}")
                    await asyncio.sleep(5)
                else:
                    # Wait out dynamic rate limit window
                    print("[~] Cooldown active. Sleeping 30s...")
                    await asyncio.sleep(30)
            except Exception as e:
                print(f"[!] Transient error: {e}. Retrying in 10s...")
                await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run_heart_loop(TARGET_VIDEO_URL, SERVICE_NAME))