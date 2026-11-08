# Code Examples

TypeScript code examples referenced from `SKILL.md`.

## Single Responsibility Principle (SRP)

// ❌ God class doing everything
class UserService {
  createUser(data) { /* ... */ }
  sendWelcomeEmail(user) { /* ... */ }
  generateReport(userId) { /* ... */ }
  syncToCRM(user) { /* ... */ }
}

// ✅ Each class has one responsibility
class UserService {
  createUser(data) { /* ... */ }
}

class EmailService {
  sendWelcomeEmail(user) { /* ... */ }
}

class ReportService {
  generateReport(userId) { /* ... */ }
}

class CRMService {
  syncUser(user) { /* ... */ }
}

## Open/Closed Principle (OCP)

// ❌ Must modify to add new discount types
function calculateDiscount(order, type) {
  if (type === 'percentage') return order.total * 0.1;
  if (type === 'fixed') return 10;
  if (type === 'seasonal') return order.total * 0.2;
  // Every new discount type requires modifying this function
}

// ✅ Extend by adding new classes
interface Discount {
  calculate(order: Order): number;
}

class PercentageDiscount implements Discount {
  constructor(private rate: number) {}
  calculate(order: Order): number {
    return order.total * this.rate;
  }
}

class FixedDiscount implements Discount {
  constructor(private amount: number) {}
  calculate(order: Order): number {
    return this.amount;
  }
}

// New discount type = new class, no modification
class LoyaltyDiscount implements Discount {
  calculate(order: Order): number {
    return order.customer.yearsActive * 5;
  }
}

## Liskov Substitution Principle (LSP)

// ❌ Square violates Rectangle's contract
class Rectangle {
  setWidth(w) { this.width = w; }
  setHeight(h) { this.height = h; }
  area() { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(w) { this.width = w; this.height = w; }
  setHeight(h) { this.width = h; this.height = h; }
}

// Code expecting Rectangle breaks with Square:
function resize(rectangle) {
  rectangle.setWidth(5);
  rectangle.setHeight(10);
  assert(rectangle.area() === 50);  // Fails with Square: area is 100
}

// ✅ Don't force inheritance where it doesn't fit
class Shape {
  area(): number { throw new Error('Not implemented'); }
}

class Rectangle extends Shape { /* independent width/height */ }
class Square extends Shape { /* single side */ }

## Interface Segregation Principle (ISP)

// ❌ Fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

// Robot forced to implement eat() and sleep()
class Robot implements Worker {
  work() { /* ... */ }
  eat() { throw new Error('Robots do not eat'); }
  sleep() { throw new Error('Robots do not sleep'); }
}

// ✅ Segregated interfaces
interface Workable { work(): void; }
interface Eatable { eat(): void; }
interface Sleepable { sleep(): void; }

class Robot implements Workable {
  work() { /* ... */ }
}

class Human implements Workable, Eatable, Sleepable {
  work() { /* ... */ }
  eat() { /* ... */ }
  sleep() { /* ... */ }
}

## Dependency Inversion Principle (DIP)

// ❌ High-level module depends on low-level module
class OrderService {
  private emailService = new SMTPEmailService();

  placeOrder(order) {
    // ... order logic
    this.emailService.sendConfirmation(order);
  }
}

// ✅ Depend on abstraction
interface EmailService {
  send(to: string, subject: string, body: string): Promise<void>;
}

class OrderService {
  constructor(private emailService: EmailService) {}

  placeOrder(order) {
    // ... order logic
    this.emailService.send(order.email, 'Order Confirmed', '...');
  }
}

// Swap implementation without touching OrderService
new OrderService(new SESEmailService());
new OrderService(new SendGridEmailService());
new OrderService(new MockEmailService());  // Testing!

## Strategy Pattern

// ❌ Growing switch statement
function calculateShipping(order, method) {
  switch (method) {
    case 'standard': return order.weight * 0.5 + 5;
    case 'express': return order.weight * 1.0 + 15;
    case 'overnight': return order.weight * 2.0 + 30;
    case 'international': return order.weight * 3.0 + 50;
    default: throw new Error(`Unknown method: ${method}`);
  }
}

// ✅ Strategy pattern
interface ShippingStrategy {
  calculate(order: Order): number;
  getEstimatedDays(): number;
}

const shippingStrategies = {
  standard: new StandardShipping(),
  express: new ExpressShipping(),
  overnight: new OvernightShipping(),
  international: new InternationalShipping(),
};

function calculateShipping(order: Order, method: string): number {
  const strategy = shippingStrategies[method];
  if (!strategy) throw new Error(`Unknown method: ${method}`);
  return strategy.calculate(order);
}

## Extract Method

// ❌ Long method with embedded logic
function printOwing(invoice) {
  // Print banner
  console.log('*******************');
  console.log('*** Customer Owes ***');
  console.log('*******************');

  // Calculate outstanding
  let outstanding = 0;
  for (const order of invoice.orders) {
    outstanding += order.amount;
  }

  // Print details
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}

// ✅ Extracted methods with descriptive names
function printOwing(invoice: Invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  printDetails(invoice, outstanding);
}

function printBanner() {
  console.log('*******************');
  console.log('*** Customer Owes ***');
  console.log('*******************');
}

function calculateOutstanding(invoice: Invoice): number {
  return invoice.orders.reduce((sum, order) => sum + order.amount, 0);
}

function printDetails(invoice: Invoice, outstanding: number) {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}

## Replace Conditional with Polymorphism

// ❌ Type-checking conditionals
function getEmployeePay(employee) {
  switch (employee.type) {
    case 'fulltime': return employee.salary;
    case 'parttime': return employee.hours * employee.hourlyRate;
    case 'contractor': return employee.hours * employee.hourlyRate * 1.1;
    case 'intern': return Math.min(employee.hours * 15, 1000);
  }
}

// ✅ Polymorphic dispatch
abstract class Employee {
  abstract getPay(): number;
}

class FullTimeEmployee extends Employee {
  getPay() { return this.salary; }
}

class PartTimeEmployee extends Employee {
  getPay() { return this.hours * this.hourlyRate; }
}

class ContractorEmployee extends Employee {
  getPay() { return this.hours * this.hourlyRate * 1.1; }
}

// New types don't require modifying existing code

## Memoization and Lazy Initialization

// Memoization
function memoize<T extends (...args: any[]) => any>(fn: T): T {
  const cache = new Map<string, ReturnType<T>>();
  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

// Lazy initialization
class ExpensiveResource {
  private _data: Data | null = null;

  get data(): Data {
    if (!this._data) {
      this._data = this.loadExpensiveData();  // Only when first accessed
    }
    return this._data;
  }
}

## Deprecated Function

/**
 * @deprecated Use calculateV2() instead. Will be removed in v3.0.
 */
function calculateV1(data: Data): number {
  console.warn('calculateV1 is deprecated. Use calculateV2.');
  return calculateV2(data);
}