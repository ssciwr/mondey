<svelte:options runes={true} />

<script lang="ts">
	import { adminUser, milestoneAgeGroups } from '$lib/admin.svelte';
	import Languages from '$lib/components/Admin/Languages.svelte';
	import Translations from '$lib/components/Admin/Translations.svelte';
	import MilestoneGroups from '$lib/components/Admin/MilestoneGroups.svelte';
	import MilestoneAgeGroups from '$lib/components/Admin/MilestoneAgeGroups.svelte';
	import Questions from '$lib/components/Admin/UserQuestions.svelte';
	import Login from '$lib/components/Admin/Login.svelte';
	import { _ } from 'svelte-i18n';
	import { onMount } from 'svelte';
	import { Tabs, TabItem } from 'flowbite-svelte';
	import {
		LanguageOutline,
		BadgeCheckOutline,
		ClipboardListOutline,
		CalendarMonthOutline
	} from 'flowbite-svelte-icons';

	onMount(async () => {
		await adminUser.refresh();
		await milestoneAgeGroups.refresh();
	});
</script>

{#if !adminUser.value || !adminUser.value.is_superuser}
	<div class="flex w-full flex-col items-center justify-center">
		<Login />
	</div>
{:else}
	<Tabs tabStyle="underline">
		{#if milestoneAgeGroups.value}
			{#each milestoneAgeGroups.value as milestoneAgeGroup (milestoneAgeGroup.id)}
				<TabItem open={milestoneAgeGroup.id === milestoneAgeGroups.value[0].id}>
					<div slot="title" class="flex items-center gap-2">
						<BadgeCheckOutline size="md" />
						{`${$_('admin.milestones')} (${milestoneAgeGroup.months_min}m-${milestoneAgeGroup.months_max}m)`}
					</div>
					<MilestoneGroups milestone_age_group_id={milestoneAgeGroup.id} />
				</TabItem>
			{/each}
		{/if}
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<ClipboardListOutline size="md" />
				{$_('admin.user-questions')}
			</div>
			<Questions />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<CalendarMonthOutline size="md" />
				{$_('admin.milestone-age-groups')}
			</div>
			<MilestoneAgeGroups />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<LanguageOutline size="md" />
				{$_('admin.translations')}
			</div>
			<Translations />
		</TabItem>
		<TabItem>
			<div slot="title" class="flex items-center gap-2">
				<LanguageOutline size="md" />
				{$_('admin.languages')}
			</div>
			<Languages />
		</TabItem>
	</Tabs>
{/if}
