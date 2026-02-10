    async def process_ppt_file(
        self,
        session,
        file_path: str,
        actual_name: str,
        llm_max_tokens: int = None,
        llm_temperature: float = None,
        llm_top_p: float = None,
        paddle_temperature: float = None,
        paddle_max_tokens: int = None,
    ):
        # 1. Конвертация PPT/PPTX в PDF
        # Используем run_in_executor, так как subprocess - блокирующая операция
        loop = asyncio.get_running_loop()
        try:
            pdf_path = await loop.run_in_executor(
                None, 
                convert_presentation_to_pdf, 
                file_path
            )
        except RuntimeError as e:
            # Здесь можно добавить логирование ошибки
            raise e

        try:
            # 2. Парсинг получившегося PDF как обычного файла
            return await self.process_single_file(
                session=session,
                pdf_path=pdf_path,
                actual_name=actual_name, # Сохраняем оригинальное имя файла презентации
                llm_max_tokens=llm_max_tokens,
                llm_temperature=llm_temperature,
                llm_top_p=llm_top_p,
                paddle_temperature=paddle_temperature,
                paddle_max_tokens=paddle_max_tokens
            )
        finally:
            # 3. Уборка: удаляем временный PDF файл после обработки
            # Проверяем, существует ли файл, перед удалением
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except OSError:
                    pass
