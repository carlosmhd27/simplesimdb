import os

import pytest

import simplesimdb as sim

# Run with pytest -s . to see stdout output

is_windows = os.name == "nt"

py_touch = "import sys; [open(arg, 'a').close() for arg in sys.argv[1:]]"


def test_construction_and_destruction():
    print("TEST")
    m = sim.Manager()
    assert os.path.isdir("data")
    m.delete_all()
    assert not os.path.isdir("data")


def test_creation():
    print("TEST CREATION")
    executable = "cp" if not is_windows else "copy"
    m = sim.Manager(directory="creation_test", executable=executable, filetype="json")
    assert m.directory == "creation_test"
    assert m.executable == executable
    assert m.filetype == "json"
    inputdata = {"Hello": "World"}
    m.create(inputdata, shell=is_windows)
    content = m.table()
    assert content == [inputdata]
    m.delete_all()
    assert not os.path.isdir(m.directory)


def test_creation_with_interpreter():
    print("TEST CREATION WITH INTERPRETER")
    script = "import sys; import shutil; shutil.copy(sys.argv[1], sys.argv[2])"
    m = sim.Manager(
        directory="creation_interpreter_test",
        executable=["python", "-c", script],
        filetype="json",
    )
    assert m.directory == "creation_interpreter_test"
    assert m.executable == ["python", "-c", script]
    assert m.filetype == "json"
    inputdata = {"Hello": "World"}
    m.create(inputdata, 0, shell=is_windows)
    content = m.table()
    assert content == [inputdata]
    m.delete_all()
    assert not os.path.isdir(m.directory)


def test_selection():
    print("TEST SELECTION")
    executable = "cp" if not is_windows else "copy"
    m = sim.Manager(directory="selection_test", executable=executable, filetype="json")
    inputdata = {"Hello": "World"}
    inputdata2 = {"Hello": "World!"}
    m.create(inputdata, shell=is_windows)
    m.create(inputdata2, shell=is_windows)
    data = m.select(inputdata)
    assert os.path.isfile(data)
    assert data == m.outfile(inputdata)
    m.delete_all()
    assert not os.path.isdir(m.directory)


def test_restart():
    print("TEST RESTART")
    executable = ["python", "-c", py_touch]
    m = sim.Manager(directory="restart_test", executable=executable, filetype="th")
    inputdata = {"Hello": "World"}
    for i in range(0, 17):
        m.create(inputdata, i)
    count = m.count(inputdata)
    assert count == 17
    data = m.select(inputdata, 3)
    assert os.path.isfile(data)
    inputdata2 = {"Hello2": "World"}
    for i in range(0, 7):
        m.create(inputdata2, i)
    content = m.table()
    # Check ordered content
    assert content == [inputdata2, inputdata]
    files = m.files()
    assert len(files) == 24
    m.delete_all()
    assert not os.path.isdir(m.directory)


def test_named_creation():
    print("TEST NAMED CREATION")
    executable = ["python", "-c", py_touch]
    m = sim.Manager(
        directory="creation_named_test", executable=executable, filetype="json"
    )
    inputdata = {"Hello": "World"}
    m.create(inputdata, 0)
    m.delete(inputdata, 0)
    m.create(inputdata, 0, "hello")
    m.create(inputdata, 1, "hello")
    content = m.table()
    print(m.files())
    assert content == [inputdata]
    m.delete_all()
    assert not os.path.isdir(m.directory)


def test_repeater():
    print("TEST REPEATER")
    os.makedirs("temp_repeater", exist_ok=True)
    executable = ["python", "-c", py_touch]
    m = sim.Repeater(executable, "temp_repeater/temp.json", "temp_repeater/temp.nc")
    inputdata = {"Hello": "World"}
    m.run(inputdata, error="display", stdout="display")
    assert os.path.isfile("temp_repeater/temp.json")
    assert os.path.isfile("temp_repeater/temp.nc")
    m.executable = "echo"
    m.run(inputdata, error="display", stdout="display", shell=is_windows)
    m.clean()
    assert not os.path.isfile("temp_repeater/temp.json")
    assert not os.path.isfile("temp_repeater/temp.nc")
    temp_folder_exists = os.path.isdir("temp_repeater")
    temp_folder_empty = not os.listdir("temp_repeater")
    if temp_folder_exists and temp_folder_empty:
        os.rmdir("temp_repeater")


def test_executable_validation():
    print("TEST EXECUTABLE VALIDATION")
    match = "Executable must be given as a string or list of strings"
    with pytest.raises(Exception, match=match):
        sim.Manager(
            directory="executable_validation_test", executable=123, filetype="json"
        )

    match = "Executable cannot be empty string or list"
    with pytest.raises(Exception, match=match):
        sim.Manager(
            directory="executable_validation_test", executable="", filetype="json"
        )

    with pytest.raises(Exception, match=match):
        sim.Manager(
            directory="executable_validation_test", executable=[], filetype="json"
        )

    m = sim.Manager(
        directory="executable_validation_test", executable="echo", filetype="json"
    )

    assert m.executable == "echo"
    m.executable = "ls -l"
    assert m.executable == "ls -l"
    m.executable = ["ls", "-l"]
    assert m.executable == ["ls", "-l"]
    m.delete_all()
    assert not os.path.isdir(m.directory)
