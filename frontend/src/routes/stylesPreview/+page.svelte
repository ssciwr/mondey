<script lang="ts">
import { goto } from "$app/navigation";
import { Button } from "flowbite-svelte";
import { BarsOutline } from "flowbite-svelte-icons";
// Example of primary button
function handleSignup() {
	goto("/signup");
}

// Example of a danger button with icon
function handleDelete() {
	// Delete logic here
}
</script>

<!-- Primary Button -->
<Button
        class="btn-primary"
        on:click={handleSignup}
>
    Sign Up
</Button>

<!-- Secondary Button -->
<Button
        class="btn-secondary"
        on:click={() => console.log('Secondary action')}
>
    Learn More
</Button>

<!-- Danger Button -->
<Button
        class="btn-danger"
        on:click={handleDelete}
>
    <BarsOutline />
</Button>

<!-- Icon Button -->
<Button
        class="btn-icon"
        on:click={() => console.log('Icon action')}
>
    <BarsOutline />
</Button>

<!-- Outlined Button with Icon -->
<Button
        outline
        class="btn-primary"
>
    <BarsOutline /> Edit Profile
</Button>

<!-- Gradient Button -->
<Button
        gradient
        color="greenToBlue"
        class="btn-secondary"
>
    Gradient Action
</Button>
