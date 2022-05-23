import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Generator, TextIO

top_str_list = []


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Tool to merge logs.')

    parser.add_argument(
        'log1',
        metavar='<PATH TO LOG1>',
        type=str,
        help='path to log to merge',
    )
    parser.add_argument(
        'log2',
        metavar='<PATH TO LOG2>',
        type=str,
        help='path to log to merge',
    )

    parser.add_argument(
        '-o', '--output',
        metavar='<PATH TO MERGED LOG>',
        help='path to merged log',
        dest='merged_log',
        required=True
    )

    parser.add_argument(
        '-f', '--force',
        action='store_const',
        const=True,
        default=False,
        help='force write logs',
        dest='force_write',
    )
    return parser.parse_args()


def _create_file(file_path: Path, *, force_write: bool = False) -> None:
    if file_path.exists():
        if not force_write:
            raise FileExistsError(
                f'File "{file_path}" already exists. Remove it first or choose another file path.')
        file_path.unlink()
    file_path.touch()


def _if_file_exist(path: Path):
    if not path.is_file():
        raise FileExistsError(
            f'File "{path}" does not exists. Choose another file path.')


def _preprocess_args(args: argparse.Namespace) -> tuple:
    merged_log = Path(args.merged_log)
    files_to_merge = list(map(Path, (args.log1, args.log2)))

    _create_file(merged_log, force_write=args.force_write)
    for log_file in files_to_merge:
        _if_file_exist(log_file)
    return merged_log, files_to_merge


def _file_reader_generator(file_path: Path) -> Generator[dict, None, None]:
    with open(file_path, 'r') as json_file:
        json_list = list(json_file)

    for json_str in json_list:
        result = json.loads(json_str)
        yield result


def _fill_output_file(list_of_generators: list, out: TextIO) -> None:
    if len(list_of_generators) == 0:
        return
    elif len(list_of_generators) == 1:
        out.write(str(top_str_list[0]))
        out.write('\n')
        while True:
            try:
                log_str = next(list_of_generators[0])
                out.write(str(log_str))
                out.write('\n')
            except StopIteration:
                return
    elif len(list_of_generators) > 1:
        while True:
            top_str_time_list = list(
                map(lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"),
                    top_str_list)
            )

            index_min = int(min(range(len(top_str_time_list)), key=top_str_time_list.__getitem__))
            out.write(str(top_str_list[index_min]))
            out.write('\n')
            try:
                top_str_list[index_min] = next(list_of_generators[index_min])
            except StopIteration:
                top_str_list.pop(index_min)
                list_of_generators.pop(index_min)
                _fill_output_file(list_of_generators, out)
                break


if __name__ == '__main__':
    args = _parse_args()
    args = _preprocess_args(args)
    merged_log, logs_to_merge = args

    logs_generators = [_file_reader_generator(log) for log in logs_to_merge]
    top_str_list = [next(gen) for gen in logs_generators]

    with open(merged_log, 'w') as out:
        _fill_output_file(logs_generators, out)
