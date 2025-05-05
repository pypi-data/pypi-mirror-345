#!/usr/bin/bash

data=$(rhjira dump --showcustomfields --showemptyfields RHEL-56971)

#@test "" {
#	run grepdata ""
#	check_status
#}

rm -rf 0001-test-dump.bats

cat << EOF >> 0001-test-dump.bats
load ./library.bats

@test "compile-rhjira" {
	cd ..
	run make
	check_status
	cp rhjira test/
}

EOF

echo "$data" | while read -r LINE
do
	# some fields have multiple [] pairs.  In order to avoid stripping the
	# wrong thing, reverse the string and cut so that we're sure we're getting
	# the 'last' ].
	name=$(echo "$LINE" | cut -d'[' -f2- | rev | cut -d"]" -f2- | rev)

	# FIXME: this doesn't work with the Development field
	[[ "$name" == "Development |"* ]] && continue

	# replace [ with \[, ] with \], " with \", and \n with \\\n
	line=$(echo "$LINE" | sed -r 's|\[|\\\[|g' | sed -r 's|\]|\\\]|g' | sed -r 's|\"|\\\"|g' | sed -r 's|\\n|\\\\\\n|g')

	echo "@test \"$name\" {"
	echo -en "\t"
	echo "run grepdumpdata \"$line\""
	echo -e "\tcheck_status"
	echo "}"
	echo ""
done >> 0001-test-dump.bats


# exit: output a nice run message

echo "To run these tests, execute:"
echo ""
echo "     bats -x --print-output-on-failure 0001-test-dump.bats"
echo ""
