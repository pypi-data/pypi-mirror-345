#!/bin/sh
case $# in
	0)
		echo "missing tool directory argument (for isort/black)" >&2
		exit 64
		;;
esac
PATH="${1}${PATH+":${PATH}"}"
export PATH
shift 1
case $# in
	0)
		set -- .
		;;
esac
isort --profile=black "$@" || exit
black --quiet "$@" || exit
#autopep8 --in-place --aggressive --aggressive --recursive "$@" || exit
