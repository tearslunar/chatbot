import os
import pandas as pd

PERSONA_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'customer_persona.csv')

class PersonaManager:
    def __init__(self, csv_path=PERSONA_CSV_PATH):
        try:
            # CSV 파일 수동 처리
            import csv
            data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # ID가 'P'로 시작하는 올바른 행만 추가
                    if row.get('ID', '').startswith('P'):
                        data.append(row)
            
            self.df = pd.DataFrame(data)
            self.df.fillna('', inplace=True)
            
            print(f"페르소나 데이터 로드 완료: {len(self.df)}개 페르소나")
            # 헤더 확인
            print("CSV 헤더:", list(self.df.columns))
            # 첫 번째 행의 데이터 확인
            if len(self.df) > 0:
                first_row = dict(self.df.iloc[0])
                print("첫 번째 페르소나 샘플:")
                for key, value in first_row.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"페르소나 CSV 파일 로드 실패: {e}")
            # 빈 DataFrame으로 초기화
            self.df = pd.DataFrame()

    def list_personas(self, keyword=None, limit=100):
        df = self.df
        if keyword:
            mask = df.apply(lambda row: keyword in str(row.values), axis=1)
            df = df[mask]
        return df.head(limit).to_dict(orient='records')

    def get_persona_by_id(self, persona_id):
        row = self.df[self.df['ID'] == persona_id]
        if not row.empty:
            return row.iloc[0].to_dict()
        return None

persona_manager = PersonaManager() 