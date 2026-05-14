import flet as ft
import duckdb


def main(page: ft.Page):
    page.title = "Asset List"
    page.padding = 16
    page.window_width = 450
    page.window_height = 530

    # 데이터베이스 접속
    con = duckdb.connect("data/finance.db")

    # 테이블 초기화 및 생성
    con.execute("DROP TABLE IF EXISTS assets")
    con.execute("""
        CREATE TABLE assets (
            ticker VARCHAR PRIMARY KEY,
            name VARCHAR,
            type VARCHAR
        )
    """)

    # CSV 데이터 삽입
    con.execute("""
        INSERT OR IGNORE INTO assets 
        SELECT * FROM read_csv_auto('data/assets.csv')
    """)

    print("데이터베이스 저장 완료")

    # 검색 함수 (순수 리스트 반환)
    def get_data_list(filter_query=""):
        if filter_query:
            query = "SELECT * FROM assets WHERE name ILIKE ? OR ticker ILIKE ?"
            search_str = f"%{filter_query}%"
            return con.execute(query, [search_str, search_str]).fetchall()
        return con.execute("SELECT * FROM assets").fetchall()

    # 행 생성 함수
    def create_rows(data_list):
        rows = []
        for row in data_list:
            ticker, name, asset_type = row
            # 이름 기반 고유 색상 생성
            name_sum = sum(ord(char) for char in str(name))
            r = (name_sum * 13) % 196 + 60
            g = (name_sum * 17) % 196 + 60
            b = (name_sum * 19) % 196 + 60
            hex_color = f"{r:02x}{g:02x}{b:02x}"

            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                ft.Image(
                                    src=f"https://placehold.jp/30/{hex_color}/000/30x30.png?text={name[:1]}",
                                    width=30,
                                    height=30,
                                ),
                                width=40,
                            ),
                            ft.Text(ticker, expand=1),
                            ft.Text(name, expand=2),
                            ft.Text(asset_type, expand=1),
                        ]
                    ),
                    height=40,
                )
            )
        return rows

    # 화면 구성
    scrollable_data = ft.Column(
        controls=create_rows(get_data_list()), scroll=ft.ScrollMode.ALWAYS, expand=True
    )

    def on_filter_change(e):
        scrollable_data.controls = create_rows(get_data_list(e.control.value))
        page.update()

    filter_input = ft.TextField(label="검색", on_change=on_filter_change)
    page.add(filter_input, ft.Divider(), scrollable_data)


if __name__ == "__main__":
    ft.run(main)
