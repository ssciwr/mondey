<svelte:options runes={true} />

<script lang="ts">
import { i18n } from "$lib/i18n.svelte";
import { Button, Heading, Input, Label } from "flowbite-svelte";

let new_email = null as string | null;
let new_password = null as string | null;
let new_password_repeat = null as string | null;
</script>

<div class="m-2 p-2 flex flex-col space-y-2 text-gray-700 dark:text-gray-400 ">
    <Heading tag="h2" class="font-bold">{i18n.tr.userData.settings}</Heading>

    <Label for="change-email" class="font-semibold text-gray-700 dark:text-gray-400">{i18n.tr.userData.changeEmail}</Label>
    <Input id="change-email" type="email"  bind:value={new_email}/>
    <Button size="lg" type="button" onclick={
        () => {
            console.log(`email change clicked ${new_email}`)
        }
    }>{i18n.tr.userData.changeEmail}</Button>

    <Label
        for={"new_password"}
        class="font-semibold text-gray-700 dark:text-gray-400"
    >{i18n.tr.userData.changePassword}</Label>
    <Input
        bind:value={new_password}
        type="password"
        id="new_password"
        autocomplete="new-password"
        placeholder={i18n.tr.userData.newPassword}
    />

    <Label
        for={"new_password-confirm"}
        class="font-semibold text-gray-700 dark:text-gray-400"
    >{i18n.tr.userData.newPasswordConfirm}</Label>
    <Input
        bind:value={new_password_repeat}
        type="password"
        id="new_password-confirm"
        autocomplete="new-password"
        placeholder={i18n.tr.userData.newPasswordConfirm}
    />
    <Button size="lg" type="button" onclick={() =>{console.log(`password change clicked ${new_password} ${new_password_repeat}` )}}>{i18n.tr.userData.changePassword}</Button>
</div>
