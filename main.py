from os import path
from Conf import prepare, cli
from Progress import progress
from Util import file


_CONFIG_FILENAME = "main.yml"


def main():

    args = cli.get_parser()
    print(f"action: {args.mode}")

    _logger, _conf = prepare.prepare(file.yaml_load_from_f(_CONFIG_FILENAME))
    _prog = progress.Progress(_logger, _conf.get("progress_filepath"))

    if not _conf or "save_point" not in _conf:
        _conf["save_point"] = _prog.new(_conf.get("job_filepath"))
        file.yaml_dump("main.yml", _conf)
        args.mode = "create"
    elif args.mode == "create":
        _prog.set(_conf.get("job_filepath"))
    elif args.mode == "destroy":
        _prog.set(path.join(_prog.get_home_dir, _conf["save_point"]))

    _prog.run(_conf["save_point"])

    if args.mode == "destroy":
        for _filename in file.get_all_file_in_dir(path.join(_prog.get_home_dir, _conf["save_point"])):
            if _filename.endswith(".yml"):
                file.remove(path.join(_prog.get_home_dir, _conf["save_point"], _filename))


if __name__ == "__main__":
    main()

