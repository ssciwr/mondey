<script>
	// @ts-nocheck
	import { base } from "$app/paths";
	
	import CardDisplay from "$lib/components//DataDisplay/CardDisplay.svelte";
	import GalleryDisplay from "$lib/components/DataDisplay/GalleryDisplay.svelte";
	import { children } from "$lib/stores/childrenStore";
	import { createDummyUser, hash, users } from "$lib/stores/userStore";
	
	import { onMount } from "svelte";
	
	export let getStarted = "";
	
	export let items = [
		{
			header: "Möchten Sie Entwicklung von Kindern begleiten und fördern?",
			summary:
				"Hier sind Sie genau richtig!",
			href: `${base}/info`,
			button: "Anmeldung",
		},
	];
	
	const props = {};
	
	onMount(async () => {
		const h = await hash("123");
		const name = "dummyUser";
		const role = "Beobachter";
		try {
			if (!users.get()[name + h + role]) {
				await createDummyUser(users);
			}
		} catch (error) {
			console.log("error in frontpage: ", error);
		}
	
		try {
			if (!children.get()[name + h + role]) {
				await children.addUser(name + h + role);
			}
		} catch (error) {
			console.log("error in frontpage: ", error);
		}
	
		try {
			await children.save();
			await users.save();
		} catch (error) {
			console.log("error in frontpage: ", error);
		}
	});
	</script>
	
	<GalleryDisplay
		withSearch={false}
		itemComponent={CardDisplay}
		data={items}
		componentProps={props}
	/>
	