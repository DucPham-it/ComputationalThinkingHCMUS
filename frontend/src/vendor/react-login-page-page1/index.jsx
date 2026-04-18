import { cloneElement, forwardRef, isValidElement } from "react";
import {
  Block,
  Button,
  Container,
  Input,
  Provider,
  Render,
  Select,
  Textarea,
  useStore
} from "react-login-page";
import "./index.css";

export * from "react-login-page";

export function Username(props) {
  const { keyname = "username", name, rename, ...elementProps } = props;
  const fieldName = name || rename || keyname;
  const fieldKey = keyname || name;

  return (
    <Input
      type="text"
      index={1}
      placeholder="Username"
      {...elementProps}
      name={fieldName}
      keyname={fieldKey}
    />
  );
}

export function Password(props) {
  const { keyname = "password", name, rename, ...elementProps } = props;
  const fieldName = name || rename || keyname;
  const fieldKey = keyname || name;

  return (
    <Input
      type="password"
      index={2}
      placeholder="Password"
      autoComplete="on"
      {...elementProps}
      name={fieldName}
      keyname={fieldKey}
    />
  );
}

export function Submit(props) {
  const { keyname = "submit", children, ...elementProps } = props;

  return (
    <Button type="submit" keyname={keyname} {...elementProps}>
      {children || "Submit"}
    </Button>
  );
}

export function Reset(props) {
  const { keyname = "reset", children, ...elementProps } = props;

  return (
    <Button type="reset" keyname={keyname} {...elementProps}>
      {children || "Reset"}
    </Button>
  );
}

export function Footer(props) {
  const { keyname = "footer", name = "footer", ...elementProps } = props;
  return <Block {...elementProps} name={keyname || name} tagName="footer" />;
}

export function Logo(props) {
  const { keyname = "logo", name = "logo", children, ...elementProps } = props;

  return (
    <Block {...elementProps} keyname={keyname || name}>
      {children || "⚛️"}
    </Block>
  );
}

export function Title(props) {
  const { keyname = "title", name = "title", children, ...elementProps } = props;

  return (
    <Block {...elementProps} keyname={keyname || name}>
      {children || "Login"}
    </Block>
  );
}

function RenderLogin() {
  const { blocks = {}, data } = useStore();
  const { fields = [], buttons = [] } = data || {};

  return (
    <Render>
      <div className="login-page-1-wrapper">
        <article>
          <header>
            {blocks.logo} {blocks.title}
          </header>
          {fields
            .sort((a, b) => a.index - b.index)
            .map((item, index) => {
              if (!item.children) return null;
              return (
                <label className={`rlp-${item.name}`} key={`${item.name}${index}`}>
                  {item.children}
                </label>
              );
            })}
          <section>
            {buttons
              .sort((a, b) => a.index - b.index)
              .map((item, index) => {
                const child = item.children;
                if (!isValidElement(child)) return null;
                return cloneElement(child, {
                  ...child.props,
                  key: `${item.name}${index}`
                });
              })}
          </section>
          {blocks.footer}
        </article>
        <div className="login-page-1-drops">
          <div />
          <div />
          <div />
          <div />
          <div />
        </div>
      </div>
    </Render>
  );
}

const LoginPage = forwardRef(function LoginPage(props, ref) {
  const { children, className, ...divProps } = props;

  return (
    <Provider>
      <Username />
      <Password />
      <Logo />
      <Title />
      <Submit />
      <Container
        {...divProps}
        ref={ref}
        className={`login-page-1 ${className || ""}`.trim()}
      >
        <RenderLogin />
        {children}
      </Container>
    </Provider>
  );
});

const Login = Object.assign(LoginPage, {
  Username,
  Password,
  Submit,
  Reset,
  Footer,
  Logo,
  Title,
  Button,
  Input,
  Select,
  Textarea
});

export default Login;
