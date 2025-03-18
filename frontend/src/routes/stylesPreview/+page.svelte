<script>
import { alertStoreSvelte } from "$lib/stores/alertStore.svelte";
import { ArrowRightAltSolid } from "flowbite-svelte-icons";

let testElementIsVisible = $state(true);
</script>

<style>
    div, .sample-button {
        margin-bottom: 100px;
        margin-top:30px;
        display: block;
    }
</style>

<div style="padding:100px">
    h1:
    <div>
        <h1 class="h1">Lorem Ipsum Dolor Sit Amet</h1>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam eget felis eget urna ultrices tincidunt.</p>
    </div>

    h2:
    <div>
        <h2 class="h2">Consectetur Adipiscing Elit</h2>
        <p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.</p>
    </div>

    h3:
    <div>
        <h3 class="h3">Nullam Eget Felis</h3>
        <p>Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante.</p>
    </div>

    text-muted
    <div>
        <h2 class="h2">Important Information</h2>
        <p class="text-muted">Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. Mauris placerat eleifend leo.</p>
    </div>

    btn-primary:
    <button class="btn-primary sample-button">
        Submit Form
    </button>

    btn-secondary:
    <button class="btn-secondary sample-button">
        Learn More
    </button>

    btn-danger:
    <button class="btn-danger sample-button">
        Delete Item
    </button>

    <hr />

    btn-primary:
    <button class="btn-primary sample-button">
        Submit Form
    </button>

    btn-secondary:
    <button class="btn-secondary sample-button">
        Learn More
    </button>

    <hr />

    <h1 class="h1">Layout examples</h1>
    panel:
    <div class="panel">
        <div>
            <h1 class="h1">Panel Layout Example</h1>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        </div>
    </div>

    panel-centred:
    <div class="panel-centered">
        <div>
            <h1 class="h1">Centered Panel Example</h1>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam.</p>
            <button class="btn-secondary"><ArrowRightAltSolid />  Contact Us</button>
        </div>
    </div>

    alert:
    <div class="panel">
        {#if testElementIsVisible}
            <h1 class="h1">Here is sample usage of the button classes and alerts.</h1>
        {/if}
        <button class="btn-primary" onclick={() => alertStoreSvelte.showAlert("Great news", "A normal alert message")}>
            Make alert appear
        </button>
        <div>
            <button class="btn-danger" onclick={() => alertStoreSvelte.showAlert("Fehler", "An error alert message, such as " +
             "caused by awaiting a promise which fails (more for devs to debug)", true)}>
                Make error appear
            </button>
        </div>
        <div>
            <button class="btn-secondary" onclick={() => alertStoreSvelte.showAlert("Click on my option to hide the title",
            "A normal alert message", false,
            () => {
                console.log('Button waas clicked..')
                testElementIsVisible = false
            })}>
                Alert with call back option
            </button>
            <span class="text-muted">(which does something when you click "Verstanden")</span>
        </div>

    </div>
</div>
