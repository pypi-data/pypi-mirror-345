"""Internationlize the Confluence page with the given page_id."""

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from confluence_utils import confluence_api
from open_ai_utils.translation import translate


I18N_LABEL_NAME = "i18n"


def internationlize_page(page_id, base_url, username, password, max_workers=2, timeout=60):
    """Internationlize the page with the given page_id."""

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        _internationlize_page(
            page_id=page_id,
            base_url=base_url,
            username=username,
            password=password,
            executor=executor,
            timeout=timeout
        )


def internationlize_pages(page_ids, base_url, username, password, max_workers=2, timeout=60):
    """Internationlize the pages with the given page_ids."""

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for page_id in page_ids:
            _internationlize_page(
                page_id=page_id,
                base_url=base_url,
                username=username,
                password=password,
                executor=executor,
                timeout=timeout
            )

            print(f"page_id={page_id}, i18n completed!")

            time.sleep(10)


def _internationlize_page(page_id, base_url, username, password,
                          executor:ThreadPoolExecutor, timeout=60):
    """Internationlize the page with the given page_id."""

    page_content = confluence_api.get_page_content(
        page_id=page_id,
        base_url=base_url,
        username=username,
        password=password
    )

    future_eng = executor.submit(translate, page_content, "Korean", "English")
    # future_chn = executor.submit(translate, page_content, "Korean", "Chinese")

    try:
        # 결과 수집 시 타임아웃 적용
        translated_eng_page_content = future_eng.result(timeout=timeout)
        # translated_chn_page_content = future_chn.result(timeout=timeout)
        print("translated completed!")
    except TimeoutError as e:
        print(f"Translation timeout! {str(e)}")
        raise e

    ui_tabs = confluence_api.generate_ui_tabs([
        confluence_api.generate_ui_tab("ENG", translated_eng_page_content),
        confluence_api.generate_ui_tab("KOR", page_content),
        # confluence_api.generate_ui_tab("CHN", translated_chn_page_content)
    ])

    print(f"page_id={page_id}")

    future_update = executor.submit(
        confluence_api.update_page,
        page_id=page_id,
        base_url=base_url,
        username=username,
        password=password,
        content=ui_tabs
    )

    future_update.result(timeout=timeout)

    future_labeling = executor.submit(
        confluence_api.add_label_to_page,
        page_id=page_id,
        label_name=I18N_LABEL_NAME,
        base_url=base_url,
        username=username,
        password=password,
    )

    future_labeling.result(timeout=timeout)
