<script lang="ts">
	import RadioList from '$lib/components/DataInput/RadioList.svelte';
	import UserLandingPage from '$lib/components/UserLandingPage.svelte';
	import { Input, Select } from 'flowbite-svelte';
	import { _ } from 'svelte-i18n';

	// this stuff here will become backend calls in the end because that is where the data this page will be filled with
	// will come from. Hence, they are not put into a separate library or anything
	function intervalRange(size: number, startAt: number = 0, step: number = 1, asItems = false) {
		let values = [...Array(size).keys()].map(
			(i) => String(i * step + startAt) + '-' + String((i + 1) * step + startAt)
		);

		if (asItems) {
			return values.map((v) => {
				return { name: String(v), value: v };
			});
		} else {
			return values;
		}
	}

	function numericalRange(size: number, startAt: number = 0, step: number = 1, asItems = false) {
		let values = [...Array(size).keys()].map((i) => i * step + startAt);

		if (asItems) {
			return values.map((v) => {
				return { name: String(v), value: v };
			});
		} else {
			return values;
		}
	}

	const userData = [
		{
			component: Select,
			value: null,
			additionalValue: null,
			props: {
				name: $_('userData.yearOfBirth.label'),
				items: numericalRange(60, 1960, 1, true),
				placeholder: $_('userData.yearOfBirth.placeholder'),
				label: $_('userData.yearOfBirth.label'),
				required: true,
				id: 'yearOfBirth'
			}
		},
		{
			component: RadioList,
			value: null,
			additionalValue: null,
			props: {
				name: $_('userData.gender.label'),
				items: [
					$_('userData.gender.items.male'),
					$_('userData.gender.items.female'),
					$_('userData.gender.items.divers'),
					$_('userData.gender.items.other')
				].map((v) => {
					return { label: String(v), value: v };
				}),
				label: $_('userData.gender.label'),
				placeholder: $_('userData.gender.placeholder'),
				required: true,
				textTrigger: $_('userData.gender.items.other'),
				selected: false,
				id: 'gender'
			}
		},
		{
			component: Select,
			value: null,
			additionalValue: null,
			props: {
				name: $_('userData.education.label'),
				items: [
					$_('userData.education.items.none'),
					$_('userData.education.items.secondarylower'),
					$_('userData.education.items.secondary'),
					$_('userData.education.items.alevel'),
					$_('userData.education.items.bsc'),
					$_('userData.education.items.msc'),
					$_('userData.education.items.phd'),
					$_('userData.education.items.other')
				].map((v) => {
					return { name: String(v), value: v };
				}),
				placeholder: $_('userData.education.placeholder'),
				required: true,
				label: $_('userData.education.label'),
				textTrigger: $_('userData.education.items.other'),
				id: 'education'
			}
		},
		{
			component: Select,
			value: null,
			additionalValue: null,
			props: {
				name: $_('userData.workingHours.label'),
				items: intervalRange(13, 0, 5, true),
				placeholder: $_('userData.workingHours.placeholder'),
				label: $_('userData.workingHours.label'),
				required: true,
				textTrigger: $_('userData.workingHours.other'),
				id: 'workingHours'
			}
		},
		{
			component: Select,
			value: null,
			additionalValue: null,
			props: {
				name: $_('userData.incomePerYear.label'),
				items: intervalRange(23, 0, 5000, true),
				placeholder: $_('userData.incomePerYear.placeholder'),
				label: $_('userData.incomePerYear.label'),
				required: true,
				textTrigger: $_('userData.incomePerYear.other'),
				id: 'incomePerYear'
			}
		},
		{
			component: Input,
			value: null,
			additionalValue: null,
			props: {
				name: $_('userData.profession.label'),
				type: 'text',
				placeholder: $_('userData.profession.placeholder'),
				label: $_('userData.profession.label'),
				required: true,
				id: 'profession'
			}
		}
	];
</script>

<UserLandingPage {userData} />
