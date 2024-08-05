#!/bin/bash
set -e
cd /project


# helpers
function _divider() {
	echo -e "\n\n\n\n\n"
}

# python deps
function _bump_reqs() {
	echo "Updating Python Dependencies"
	pip install bumper --upgrade > /dev/null
	bump
}

# nims
function _bump_nims() {
	echo "Updating NIMs"
	for app in apps/*.sh; do
		# get application image
		export IMAGE=$(env -i /bin/bash $app image 2> /dev/null)
		export TAG=$(env -i /bin/bash $app tag 2> /dev/null)

		# ensure this is a nim
		if [[ "$IMAGE" != "nvcr.io/nim/"* ]]; then
			continue
		fi

		# find the latest tag
		LATEST=$( \
			skopeo list-tags docker://$IMAGE | \
			jq '.Tags' | \
			jq -r '.[] | select(contains("sha256") | not)' | \
			grep -v 'latest' | \
			tail -n 1)

		# check if an update is required
		if [ "${LATEST}x" != "${TAG}x" ]; then
			echo "Updating: $app [ $TAG -> $LATEST ]"
			sed -i -r 's/(^TAG=.*)"'$TAG'"\)/\1"'$LATEST'")/g' "$app"
			git diff "$app"
		else
			echo "NO CHANGE"
			echo "$TAG == $LATEST"
		fi
		echo ""
	done
}

main() {
	_bump_reqs
	_divider
	_bump_nims
}

main
