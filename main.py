import os
import sys
from config import Config
from llm_client import llm_client
from objection_trainer import ObjectionTrainer


def clear_screen():
    "Очищает экран терминала"
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    "Печатает заголовок с рамкой"
    print("\n" + "-" * 10)
    print(f" {text}")
    print("-" * 10)


def print_score(score, max_score=10):
    "Печатает шкалу оценки"
    filled = "█" * score
    empty = "░" * (max_score - score)
    print(f"[{filled}{empty}] {score}/10")


def main():
    trainer = ObjectionTrainer(llm_client)

    while True:
        clear_screen()
        print_header("Тенажёр по продажам")

        print("\nВыберите тип клиента:")
        print("1. Скептик (всё отрицает, просит доказательства)")
        print("2. Занятой (вечно спешит, нет времени)")
        print("3. Экономный (считает каждую копейку)")
        print("4. Агрессивный (грубит и хамит)")
        print("5. Статистика использования")
        print("6. Выход")

        choice = input("\nВаш выбор (1-6): ").strip()

        if choice == '6':
            print("\nДо встречи!")
            break

        if choice == '5':
            clear_screen()
            print_header("Статистика")
            print("\n" + llm_client.get_stats())
            input("\nНажмите Enter для возврата в меню")
            continue

        client_types = {
            '1': 'skeptic',
            '2': 'busy',
            '3': 'economical',
            '4': 'aggressive'
        }

        if choice not in client_types:
            input("\nНеверный выбор. Нажмите Enter")
            continue

        client_type = client_types[choice]
        client_name = Config.CLIENT_TYPES[client_type]['name']

        #Начинаем тренировку
        trainer.start_training(client_type)

        while True:
            clear_screen()
            print_header(f"Общение с {client_name.upper()}")

            #Прогресс
            progress = trainer.get_progress()
            print(f"\nПрогресс: {progress['completed']}/{progress['total']} ({progress['percent']}%)")

            #Совет
            tip, is_fallback_tip = llm_client.generate_tip(client_type)
            if is_fallback_tip:
                print(f"\n💡 Совет (из базы): {tip}")
            else:
                print(f"\n💡 Совет (ЛЛМ): {tip}")

            #Возражение
            objection = trainer.current_objection
            print(f"\nКлиент: \"{objection}\"")

            # Ответ
            print("\nВаш ответ (или 'меню' для выхода, 'далее' пропустить):")
            answer = input("> ").strip()

            if answer.lower() == 'меню':
                break
            elif answer.lower() == 'далее':
                trainer.get_next_objection()
                continue
            elif not answer:
                print("\nОтвет не может быть пустым!")
                input("Нажмите Enter")
                continue

            #Сохраняем ответ
            trainer.add_answer(answer)

            #Получаем оценку
            print("\nАнализируем ответ")
            evaluation = llm_client.evaluate_answer(client_type, objection, answer)

            #Показываем результаты
            print("\n" + "-" * 10)
            if evaluation.get('from_fallback', True):
                print("Оценка(базовый анализ):")
            else:
                print("Оценка(ЛЛМ):")
            # print("-" * 10)
            #
            # print(f"\nЭмпатия:          ", end="")
            # print_score(evaluation['scores']['empathy'])
            #
            # print(f"Аргументация:     ", end="")
            # print_score(evaluation['scores']['arguments'])
            #
            # print(f"Работа с возраж.: ", end="")
            # print_score(evaluation['scores']['objection_handling'])
            #
            # print(f"Тон общения:      ", end="")
            # print_score(evaluation['scores']['tone'])
            #
            # print(f"\nИтог: {evaluation['total']}/10")

            print(f"\nКомментарий:")
            print(f"{evaluation['feedback']}")

            if evaluation['good_points']:
                print(f"\nЧто получилось:")
                for point in evaluation['good_points']:
                    print(f"  • {point}")

            if evaluation['improvements']:
                print(f"\nИсправить:")
                for imp in evaluation['improvements']:
                    print(f"  • {imp}")

            print("\n" + "-" * 10)




            if progress['completed'] >= progress['total']:
                print("\nВы отработали все возражения")
                input("\nНажмите Enter для выбора нового клиента")
                break

            input("\nНажмите Enter для следующего возражения")
            trainer.get_next_objection()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nДо свидания!")
        sys.exit(0)