load ./library.bats

setup_file() {
	echo "********************************************" >&3
	echo "Running tests in $BATS_TEST_FILENAME" >&3
	echo "********************************************" >&3

	[ -e ./rhjira ] && rm -f ./rhjira
	cp ../bin/rhjira .

	export epicid="TP-14858"
	export bugid="TP-14864"
	export featureid="TP-14861"
}

#Assignee:
@test "clearandset Epic" {
	r1=("assignee" "Assignee:" "prarit@redhat.com")
	r2=("components" "Components:" "Documentation, test1")
	r3=("affectsversion" "Affects Versions:" "1.0.0 Beta, 4.11")
	r4=("fixversion" "Fix Versions:" "1.0.0 Beta, 4.11")
	r5=("contributors" "Contributors:" "prarit@redhat.com, rhel-ai-jira-bot")
	r6=("releaseblocker" "Release Blocker:" "Rejected")
	# severity cannot be set in TP
	r8=("parentlink" "Parent Link:" "TP-14861")

	all_rows=(r1 r2 r3 r4 r5 r6 r8)

	# Loop through each record
	for row_name in "${all_rows[@]}"; do
		eval "row=(\"\${${row_name}[@]}\")"
		argument="${row[0]}"
		header="${row[1]}"
		value="${row[2]}"

		./rhjira edit --${argument} "" --noeditor $epicid
		grepstr=$(./rhjira show $epicid | grep "$header")
		echo "***********"
		echo "Clearing $argument"
		echo "grepstr = |$grepstr|"
		echo "argument=$argument header=$header value=$value"
		echo "***********"
		run [ "$grepstr" == "${header} " ]
		check_status

		echo "Setting $argument"
		./rhjira edit --${argument} "${value}" --noeditor $epicid
		grepstr=$(./rhjira show $epicid | grep "$header")
		echo "***********"
		echo "Setting $argument"
		echo "grepstr = |$grepstr|"
		echo "argument=$argument header=$header value=$value"
		echo "***********"
		run [ "$grepstr" == "${header} ${value}" ]
		check_status
	done
}

@test "clearandset Bug" {
	r1=("assignee" "Assignee:" "prarit@redhat.com")
	r2=("components" "Components:" "Documentation, test1")
	r3=("affectsversion" "Affects Versions:" "1.0.0 Beta, 4.11")
	r4=("fixversion" "Fix Versions:" "1.0.0 Beta, 4.11")
	r5=("contributors" "Contributors:" "prarit@redhat.com, rhel-ai-jira-bot")
	r6=("releaseblocker" "Release Blocker:" "Rejected")
	# severity cannot be set in TP
	r9=("epiclink" "Epic Link:" $epicid)
	r10=("gitpullrequest" "Git Pull Request:" "https://redhat.com")

	all_rows=(r1 r2 r3 r4 r5 r6 r9 r10)

	# Loop through each record
	for row_name in "${all_rows[@]}"; do
		eval "row=(\"\${${row_name}[@]}\")"
		argument="${row[0]}"
		header="${row[1]}"
		value="${row[2]}"

		./rhjira edit --${argument} "" --noeditor $bugid
		grepstr=$(./rhjira show $bugid | grep "$header")
		echo "***********"
		echo "Clearing $argument"
		echo "grepstr = |$grepstr|"
		echo "argument=$argument header=$header value=$value"
		echo "***********"
		run [ "$grepstr" == "${header} " ]
		check_status

		echo "Setting $argument"
		./rhjira edit --${argument} "${value}" --noeditor $bugid
		grepstr=$(./rhjira show $bugid | grep "$header")
		echo "***********"
		echo "Setting $argument"
		echo "grepstr = |$grepstr|"
		echo "argument=$argument header=$header value=$value"
		echo "***********"
		run [ "$grepstr" == "${header} ${value}" ]
		check_status
	done
}
