import argparse
from generators.leak_generator.leak_generator import LeaksGenerator

def main():
  parser = argparse.ArgumentParser(prog='Генератор задач')
  parser.add_argument('-m', '--mode', help='Генерация задачи или проверка')
  # parser.add_argument('-f', '--function', help='Функция, в которой будет ошибка')

  args = parser.parse_args()
  # print(args, args.mode)
  if args.mode == "1":
    generator = LeaksGenerator(3)
    generator.create_task()
  elif args.mode == "2":
    generator = LeaksGenerator(3)
    generator.verify_task()


if __name__ == "__main__":
    main()